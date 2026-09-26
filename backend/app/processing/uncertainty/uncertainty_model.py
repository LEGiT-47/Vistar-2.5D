"""Transparent Uncertainty and Trust Modeling Engine.
Quantifies perception uncertainty and system trust score [0, 100].
"""

from typing import Dict, Any, Optional
import numpy as np

class UncertaintyModel:
    def __init__(self):
        # Configurable weights summing to 1.0
        self.w_density = 0.20
        self.w_semantic = 0.25
        self.w_terrain = 0.15
        self.w_sensor = 0.20
        self.w_dem = 0.20

    def compute_cell_uncertainty(
        self,
        point_count: int,
        sensor_confidence: float,
        semantic_confidence: float,
        terrain_roughness: float,
        dynamic_prob: float,
        dem_diff_m: Optional[float] = None
    ) -> Dict[str, float]:
        """Calculates normalized uncertainty metrics for a single 2.5D cell."""
        # 1. Point density uncertainty: higher point count -> lower uncertainty
        # Plateau around 20 points per cell
        u_density = float(np.clip(1.0 - (point_count / 20.0), 0.0, 1.0))

        # 2. Sensor confidence uncertainty
        u_sensor = float(np.clip(1.0 - sensor_confidence, 0.0, 1.0))

        # 3. Semantic uncertainty
        u_semantic = float(np.clip(1.0 - semantic_confidence, 0.0, 1.0))

        # 4. Terrain complexity uncertainty (roughness / micro-topography)
        u_terrain = float(np.clip(terrain_roughness / 0.20, 0.0, 1.0))

        # 5. DEM disagreement uncertainty
        if dem_diff_m is not None:
            u_dem = float(np.clip(abs(dem_diff_m) / 1.5, 0.0, 1.0))
        else:
            u_dem = 0.25  # Neutral fallback when DEM isn't present

        # Weighted uncertainty score in [0, 1]
        raw_u = (
            self.w_density * u_density +
            self.w_sensor * u_sensor +
            self.w_semantic * u_semantic +
            self.w_terrain * u_terrain +
            self.w_dem * u_dem
        )
        uncertainty_score = float(np.clip(raw_u, 0.0, 1.0))

        # Trust score in [0, 100]
        # High dynamic content also reduces localized static trust
        dynamic_penalty = dynamic_prob * 0.15
        trust_val = (1.0 - uncertainty_score) * 100.0 - (dynamic_penalty * 100.0)
        trust_score = float(np.clip(trust_val, 0.0, 100.0))

        return {
            "uncertainty_score": round(uncertainty_score, 3),
            "trust_score": round(trust_score, 1),
            "u_density": round(u_density, 3),
            "u_sensor": round(u_sensor, 3),
            "u_semantic": round(u_semantic, 3),
            "u_terrain": round(u_terrain, 3),
            "u_dem": round(u_dem, 3)
        }

    def compute_mission_trust_score(
        self,
        avg_density: float,
        low_confidence_ratio: float,
        dem_agreement_score: float,
        dynamic_ratio: float
    ) -> float:
        """Computes global mission-level trust score [0, 100]."""
        # Baseline trust from density (0 to 40)
        density_pts = min(40.0, (avg_density / 30.0) * 40.0)
        # Trust from clear returns (0 to 30)
        clear_pts = max(0.0, (1.0 - low_confidence_ratio) * 30.0)
        # Trust from DEM agreement (0 to 30)
        dem_pts = (dem_agreement_score / 100.0) * 30.0

        raw_trust = density_pts + clear_pts + dem_pts - (dynamic_ratio * 15.0)
        return float(np.clip(round(raw_trust, 1), 5.0, 98.5))
