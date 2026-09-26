"""Dynamic Object Detection and Temporal Filtering.
Distinguishes transient/moving actors (vehicles, pedestrians, cyclists) from permanent terrain features.
Dynamic objects remain visible in the active live view but are excluded from the persistent 2.5D terrain grid.
"""

from typing import Dict, Any, Tuple, Optional, List
import numpy as np
from ..semantics.ontology import SemanticClass

class DynamicObjectDetector:
    def __init__(self, velocity_threshold: float = 0.5):
        self.velocity_threshold = velocity_threshold
        # Track history for centroid displacement matching: dict of id -> (centroid, timestamp)
        self.track_history: Dict[int, Tuple[np.ndarray, float]] = {}

    def analyze_dynamics(
        self,
        points: np.ndarray,
        semantic_labels: np.ndarray,
        instance_ids: Optional[np.ndarray] = None,
        dynamic_labels: Optional[np.ndarray] = None,
        timestamp: float = 0.0
    ) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
        """Calculates dynamic_probability in [0, 1] for every point.
        
        Returns:
            dynamic_prob: N array in [0, 1]
            is_dynamic_mask: boolean mask (True for dynamic)
            metrics: dynamic object count and breakdown
        """
        n_pts = len(points)
        if n_pts == 0:
            return np.zeros(0, dtype=np.float32), np.zeros(0, dtype=bool), {}

        dynamic_prob = np.zeros(n_pts, dtype=np.float32)

        # Baseline semantic prior: naturally movable classes
        movable_mask = np.isin(semantic_labels, [
            SemanticClass.VEHICLE,
            SemanticClass.PEDESTRIAN,
            SemanticClass.CYCLIST
        ])

        # If dataset provides explicit dynamic labels (e.g. SemanticKITTI moving vehicle class)
        if dynamic_labels is not None and len(dynamic_labels) == n_pts:
            dynamic_prob[dynamic_labels > 0] = 0.95
            dynamic_prob[(dynamic_labels == 0) & movable_mask] = 0.35  # Parked/static vehicle
        else:
            # Base prior for movable classes
            dynamic_prob[movable_mask] = 0.75
            # Fast heuristic: points higher than ground and forming isolated clusters
            dynamic_prob[semantic_labels == SemanticClass.PEDESTRIAN] = 0.85
            dynamic_prob[semantic_labels == SemanticClass.CYCLIST] = 0.90

        # Multi-frame instance centroid displacement check if instances are supplied
        if instance_ids is not None and len(instance_ids) == n_pts:
            unique_instances = np.unique(instance_ids[instance_ids > 0])
            for inst_id in unique_instances:
                inst_mask = (instance_ids == inst_id)
                inst_pts = points[inst_mask, :3]
                if len(inst_pts) < 5:
                    continue
                centroid = np.mean(inst_pts, axis=0)
                
                if inst_id in self.track_history:
                    prev_centroid, prev_t = self.track_history[inst_id]
                    dt = max(0.01, timestamp - prev_t)
                    dist = np.linalg.norm(centroid[:2] - prev_centroid[:2])
                    speed = dist / dt
                    if speed > self.velocity_threshold:
                        dynamic_prob[inst_mask] = min(1.0, 0.6 + 0.4 * min(1.0, speed / 5.0))
                    else:
                        dynamic_prob[inst_mask] = max(0.1, dynamic_prob[inst_mask] * 0.5)

                self.track_history[inst_id] = (centroid, timestamp)

        # Static permanent terrain features cannot be dynamic
        static_environment_mask = np.isin(semantic_labels, [
            SemanticClass.GROUND,
            SemanticClass.ROAD,
            SemanticClass.GRASS,
            SemanticClass.MUD,
            SemanticClass.WATER,
            SemanticClass.BUILDING,
            SemanticClass.WALL
        ])
        dynamic_prob[static_environment_mask] = 0.0

        is_dynamic = dynamic_prob >= 0.50

        metrics = {
            "dynamic_point_count": int(np.sum(is_dynamic)),
            "static_point_count": int(n_pts - np.sum(is_dynamic)),
            "dynamic_ratio": round(float(np.sum(is_dynamic) / max(1, n_pts)), 3),
            "tracked_instances": len(self.track_history)
        }
        return dynamic_prob, is_dynamic, metrics
