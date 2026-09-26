"""Terrain analysis, surface normal calculation, roughness estimation, and hazard classification.
Identifies POTHOLE, WALL, STEEP_SLOPE, ROUGH_TERRAIN, WATER, OBSTACLE, and UNKNOWN hazards.
"""

from enum import Enum
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from ..semantics.ontology import SemanticClass

class TerrainHazard(str, Enum):
    SAFE = "SAFE"
    POTHOLE = "POTHOLE"
    WALL = "WALL"
    STEEP_SLOPE = "STEEP_SLOPE"
    ROUGH_TERRAIN = "ROUGH_TERRAIN"
    WATER = "WATER"
    OBSTACLE = "OBSTACLE"
    UNKNOWN = "UNKNOWN"

class TerrainAnalyzer:
    def __init__(
        self,
        slope_threshold_deg: float = 18.0,
        roughness_threshold: float = 0.12,
        obstacle_height_threshold: float = 0.35,
        pothole_depth_threshold: float = -0.15
    ):
        self.slope_threshold_deg = slope_threshold_deg
        self.roughness_threshold = roughness_threshold
        self.obstacle_height_threshold = obstacle_height_threshold
        self.pothole_depth_threshold = pothole_depth_threshold

    def analyze_cell(
        self,
        z_values: np.ndarray,
        dominant_semantic_class: int,
        dynamic_prob: float,
        sensor_confidence: float,
        ground_ref_z: float = -1.6,
        surface_normal: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """Calculates terrain properties and hazard classification for a 2.5D cell."""
        if len(z_values) == 0:
            return {
                "elevation_mean": ground_ref_z,
                "elevation_min": ground_ref_z,
                "elevation_max": ground_ref_z,
                "slope_deg": 0.0,
                "roughness": 0.0,
                "obstacle_height": 0.0,
                "hazard": TerrainHazard.UNKNOWN,
                "traversability": 0.5
            }

        elev_mean = float(np.mean(z_values))
        elev_min = float(np.min(z_values))
        elev_max = float(np.max(z_values))
        roughness = float(np.std(z_values))
        height_span = elev_max - elev_min

        # Estimate slope from surface normal if provided, or gradient
        if surface_normal is not None and np.linalg.norm(surface_normal) > 1e-4:
            # Angle with vertical unit vector [0, 0, 1]
            cos_theta = np.clip(abs(surface_normal[2]) / np.linalg.norm(surface_normal), 0.0, 1.0)
            slope_deg = float(np.degrees(np.arccos(cos_theta)))
        else:
            slope_deg = float(min(45.0, height_span * 25.0))

        # Obstacle height relative to nominal ground
        obs_height = max(0.0, elev_max - ground_ref_z)

        # Hazard detection rules
        hazard = TerrainHazard.SAFE

        if dominant_semantic_class == SemanticClass.WATER:
            hazard = TerrainHazard.WATER
        elif obs_height > 1.2 and height_span > 0.8:
            hazard = TerrainHazard.WALL
        elif obs_height > self.obstacle_height_threshold:
            hazard = TerrainHazard.OBSTACLE
        elif (elev_mean - ground_ref_z) < self.pothole_depth_threshold and roughness > 0.06:
            hazard = TerrainHazard.POTHOLE
        elif slope_deg > self.slope_threshold_deg:
            hazard = TerrainHazard.STEEP_SLOPE
        elif roughness > self.roughness_threshold:
            hazard = TerrainHazard.ROUGH_TERRAIN
        elif sensor_confidence < 0.35:
            hazard = TerrainHazard.UNKNOWN

        return {
            "elevation_mean": round(elev_mean, 3),
            "elevation_min": round(elev_min, 3),
            "elevation_max": round(elev_max, 3),
            "slope_deg": round(slope_deg, 2),
            "roughness": round(roughness, 3),
            "obstacle_height": round(obs_height, 3),
            "hazard": hazard.value
        }
