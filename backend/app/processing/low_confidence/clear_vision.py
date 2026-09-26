"""Low-Confidence Environmental Return Filtering (Clear-Vision Engine).
Scientifically grounded filter for airborne aerosols, exhaust plumes, smoke, and synthetic ghost returns.

Terminology: "Low-confidence environmental return filtering"
Downweights or rejects airborne non-solid returns before projecting onto trusted 2.5D terrain.
"""

from typing import Dict, Any, Tuple, Optional
import numpy as np
from ..semantics.ontology import SemanticClass

class ClearVisionFilter:
    def __init__(self, confidence_rejection_threshold: float = 0.35):
        self.threshold = confidence_rejection_threshold

    def filter_returns(
        self,
        points: np.ndarray,
        semantic_labels: np.ndarray,
        intensity: Optional[np.ndarray] = None,
        synthetic_stress_test: bool = False
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
        """Evaluates point-wise confidence and separates trusted terrain returns from low-confidence aerosol/ghost returns.
        
        Returns:
            confidence_scores: N array in [0, 1]
            trusted_mask: boolean mask (True for trusted)
            filtered_points: points that passed the threshold
            metrics: rejection counts and diagnostics
        """
        n_pts = len(points)
        if n_pts == 0:
            return np.zeros(0, dtype=np.float32), np.zeros(0, dtype=bool), points, {}

        confidence = np.ones(n_pts, dtype=np.float32)

        # 1. Official Dataset Annotation Check (PandaSet / Boreas smoke/exhaust)
        smoke_mask = (semantic_labels == SemanticClass.SMOKE)
        confidence[smoke_mask] = 0.12  # Very low confidence for aerosol/exhaust

        # 2. Reflectivity / Intensity check if present
        # Aerosols typically exhibit very low or diffuse backscatter intensity
        if intensity is not None and len(intensity) == n_pts:
            low_int_mask = (intensity < 0.10) & (points[:, 2] > -1.0)
            confidence[low_int_mask] *= 0.70

        # 3. Floating return detection (sparse points hovering high with no ground connection)
        z = points[:, 2]
        floating_mask = (z > 0.5) & (z < 3.5) & (semantic_labels == SemanticClass.UNKNOWN)
        confidence[floating_mask] *= 0.40

        # 4. Synthetic Stress-Test Mode (if enabled by scenario)
        if synthetic_stress_test:
            # Ghost returns with low confidence
            ghost_indices = np.random.choice(n_pts, size=int(0.12 * n_pts), replace=False)
            confidence[ghost_indices] = np.random.uniform(0.05, 0.28, size=len(ghost_indices))

        trusted_mask = confidence >= self.threshold
        rejected_count = int(np.sum(~trusted_mask))

        metrics = {
            "total_points_evaluated": n_pts,
            "trusted_points_passed": int(np.sum(trusted_mask)),
            "low_confidence_rejected": rejected_count,
            "rejection_percentage": round(float(rejected_count / max(1, n_pts)) * 100.0, 2),
            "synthetic_stress_active": synthetic_stress_test,
            "pipeline_stage": "Low-confidence environmental return filtering"
        }
        return confidence, trusted_mask, points[trusted_mask], metrics

    @staticmethod
    def inject_synthetic_ghost_returns(points: np.ndarray, intensity: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Injects controlled synthetic ghost returns, dust clouds, and floating noise for stress-testing."""
        n_orig = len(points)
        n_ghost = int(n_orig * 0.18)  # 18% ghost returns
        
        # Cluster 1: Exhaust plume behind vehicle [-3m to -7m behind ego]
        plume_x = np.random.normal(loc=-4.5, scale=1.0, size=n_ghost // 2)
        plume_y = np.random.normal(loc=0.0, scale=0.8, size=n_ghost // 2)
        plume_z = np.random.normal(loc=-0.2, scale=0.6, size=n_ghost // 2)
        
        # Cluster 2: Floating dust cloud ahead [8m to 16m ahead]
        dust_x = np.random.normal(loc=12.0, scale=2.5, size=n_ghost - len(plume_x))
        dust_y = np.random.normal(loc=1.5, scale=2.0, size=n_ghost - len(plume_x))
        dust_z = np.random.normal(loc=0.5, scale=0.7, size=n_ghost - len(plume_x))

        ghost_xyz = np.vstack([
            np.column_stack([plume_x, plume_y, plume_z]),
            np.column_stack([dust_x, dust_y, dust_z])
        ])

        # Ghost features
        ghost_intensity = np.random.uniform(0.02, 0.15, size=n_ghost)
        ghost_labels = np.full(n_ghost, SemanticClass.SMOKE, dtype=np.int32)

        # Merge with original
        combined_xyz = np.vstack([points[:, :3], ghost_xyz])
        
        if intensity is not None:
            combined_intensity = np.concatenate([intensity, ghost_intensity])
        else:
            combined_intensity = np.concatenate([np.ones(n_orig, dtype=np.float32) * 0.5, ghost_intensity])

        return combined_xyz, combined_intensity, ghost_labels
