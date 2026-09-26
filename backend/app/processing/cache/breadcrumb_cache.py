"""Smart Map Cache / Digital Breadcrumb Engine.
Maintains persistent compact historical map of traversed mission terrain.
Deduplicates cells, compresses historical memory, and enables safe backtracking during 'SENSOR DEGRADED' events.
"""

from typing import Dict, Any, List, Optional
import numpy as np

class BreadcrumbCacheEngine:
    def __init__(self, raw_bytes_per_point: int = 16):
        # 16 bytes per raw point: [x(float32), y(float32), z(float32), intensity(uint16), timestamp(uint16)]
        self.raw_bytes_per_point = raw_bytes_per_point
        # Historical cached cells: key -> cell dict
        self.cached_cells: Dict[str, Dict[str, Any]] = {}
        self.trajectory_poses: List[List[float]] = []  # [[x, y, z, timestamp], ...]
        self.cumulative_distance_m: float = 0.0
        self.cumulative_raw_points: int = 0
        self.is_sensor_degraded: bool = False

    def update_cache(
        self,
        current_cells: Dict[str, Any],
        ego_pose: Optional[Dict[str, float]],
        frame_raw_point_count: int,
        timestamp: float = 0.0
    ) -> Dict[str, Any]:
        """Appends visited map regions, updates timestamps, and deduplicates overlapping cells."""
        # Update ego pose & odometer
        if ego_pose:
            px = ego_pose.get("x", 0.0)
            py = ego_pose.get("y", 0.0)
            pz = ego_pose.get("z", 0.0)
            if len(self.trajectory_poses) > 0:
                last_p = self.trajectory_poses[-1]
                step = np.hypot(px - last_p[0], py - last_p[1])
                self.cumulative_distance_m += step
            self.trajectory_poses.append([px, py, pz, timestamp])

        self.cumulative_raw_points += frame_raw_point_count

        # Merge cells into historical cache (deduplicate by spatial key)
        for key, cell in current_cells.items():
            cell_dict = cell.to_dict() if hasattr(cell, 'to_dict') else cell
            # Only cache static terrain cells (exclude transient dynamic objects)
            if cell_dict.get("dynamic_probability", 0.0) < 0.40:
                self.cached_cells[key] = {
                    "x": cell_dict["x"],
                    "y": cell_dict["y"],
                    "resolution": cell_dict["resolution"],
                    "elevation_mean": cell_dict["elevation_mean"],
                    "traversability": cell_dict["traversability"],
                    "semantic_class": cell_dict["semantic_class"],
                    "timestamp": timestamp
                }

        return self.get_cache_metrics()

    def trigger_sensor_degradation(self) -> Dict[str, Any]:
        """Simulates SENSOR DEGRADED event: LiDAR returns fail or suffer heavy attenuation,
        retaining historical breadcrumb cache for autonomous retreat / backtrack corridor.
        """
        self.is_sensor_degraded = True
        return {
            "sensor_status": "DEGRADED",
            "message": "LiDAR field-of-view attenuated. Retaining historical 2.5D breadcrumb cache for backtrack corridor.",
            "historical_cells_retained": len(self.cached_cells),
            "backtrack_available": True
        }

    def restore_sensor(self) -> Dict[str, Any]:
        self.is_sensor_degraded = False
        return {"sensor_status": "NOMINAL", "message": "LiDAR returns restored."}

    def get_cache_metrics(self) -> Dict[str, Any]:
        """Calculates factual cache size, raw equivalent, and compression ratio."""
        cached_count = len(self.cached_cells)
        # Each cached cell representation: ~32 bytes (x, y, z, res, trav, semantic, time)
        cache_size_bytes = cached_count * 32
        
        # Raw point cloud equivalent
        raw_equiv_bytes = self.cumulative_raw_points * self.raw_bytes_per_point
        
        # Area estimation (sum of cell areas)
        cached_area_m2 = 0.0
        for cell in self.cached_cells.values():
            res = cell.get("resolution", 0.20)
            cached_area_m2 += res * res

        compression_ratio = round(raw_equiv_bytes / max(1, cache_size_bytes), 1)

        return {
            "cached_cell_count": cached_count,
            "cached_area_m2": round(cached_area_m2, 1),
            "cache_size_bytes": cache_size_bytes,
            "cache_size_kb": round(cache_size_bytes / 1024.0, 1),
            "cache_size_mb": round(cache_size_bytes / (1024.0 * 1024.0), 3),
            "cumulative_raw_points": self.cumulative_raw_points,
            "raw_equivalent_bytes": raw_equiv_bytes,
            "raw_equivalent_mb": round(raw_equiv_bytes / (1024.0 * 1024.0), 2),
            "compression_ratio": compression_ratio,
            "mission_distance_m": round(self.cumulative_distance_m, 1),
            "sensor_degraded": self.is_sensor_degraded,
            "breadcrumb_waypoints": len(self.trajectory_poses)
        }
