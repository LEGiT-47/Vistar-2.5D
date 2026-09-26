"""Adaptive Foveated Grid Engine.
Core VISTAR-2.5D innovation: Variable resolution terrain cells {0.05, 0.10, 0.20, 0.50} meters
allocated by distance foveation, terrain complexity, obstacle risk, and uncertainty refinement.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import time

from ..semantics.ontology import SemanticClass, get_traversability_base
from ..terrain.terrain_analyzer import TerrainAnalyzer, TerrainHazard
from ..uncertainty.uncertainty_model import UncertaintyModel

RESOLUTIONS = [0.05, 0.10, 0.20, 0.50]  # meters

@dataclass
class Cell25D:
    x: float
    y: float
    resolution: float
    elevation_mean: float
    elevation_min: float
    elevation_max: float
    occupancy: float              # 0.0 (free) to 1.0 (fully occupied)
    semantic_class: int
    slope_deg: float
    roughness: float
    traversability: float         # 0.0 (blocked) to 1.0 (safe)
    dynamic_probability: float
    confidence: float
    uncertainty: float
    hazard: str
    point_count: int
    is_refined: bool = False
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class AdaptiveFoveatedGridEngine:
    def __init__(
        self,
        refinement_slope_thresh: float = 14.0,
        refinement_roughness_thresh: float = 0.08,
        refinement_uncertainty_thresh: float = 0.55,
        refinement_obs_risk_thresh: float = 0.40
    ):
        self.refinement_slope_thresh = refinement_slope_thresh
        self.refinement_roughness_thresh = refinement_roughness_thresh
        self.refinement_uncertainty_thresh = refinement_uncertainty_thresh
        self.refinement_obs_risk_thresh = refinement_obs_risk_thresh
        self.terrain_analyzer = TerrainAnalyzer()
        self.uncertainty_model = UncertaintyModel()

    def get_base_resolution(self, dist_xy: float) -> float:
        """Determines base distance foveation tier."""
        if dist_xy <= 10.0:
            return 0.05   # 5 cm high-definition near-field
        elif dist_xy <= 25.0:
            return 0.10   # 10 cm mid-near field
        elif dist_xy <= 50.0:
            return 0.20   # 20 cm mid-far field
        else:
            return 0.50   # 50 cm far field

    def refine_resolution(self, current_res: float) -> float:
        """Refines to next finer resolution tier."""
        if current_res == 0.50:
            return 0.20
        elif current_res == 0.20:
            return 0.10
        elif current_res == 0.10:
            return 0.05
        return 0.05

    def build_adaptive_grid(
        self,
        points: np.ndarray,
        semantic_labels: np.ndarray,
        dynamic_probs: np.ndarray,
        confidence_scores: np.ndarray,
        timestamp: float = 0.0,
        ground_ref_z: float = -1.6
    ) -> Tuple[Dict[str, Cell25D], Dict[str, Any]]:
        """Projects points into sparse multi-resolution 2.5D cells with adaptive refinement.
        
        Returns:
            cells: Dict of cell_key -> Cell25D
            metrics: breakdown of cells by resolution, memory, timing
        """
        t0 = time.perf_counter()
        n_pts = len(points)
        if n_pts == 0:
            return {}, {"total_cells": 0, "time_ms": 0.0}

        xyz = points[:, :3]
        dists = np.linalg.norm(xyz[:, :2], axis=1)

        # Step 1: Assign initial base resolution to each point according to radial distance
        base_res_tiers = np.where(dists <= 10.0, 0.05,
                         np.where(dists <= 25.0, 0.10,
                         np.where(dists <= 50.0, 0.20, 0.50)))

        # Temporary spatial bucket dictionary: (bucket_x, bucket_y, res) -> list of point indices
        buckets: Dict[Tuple[int, int, float], List[int]] = {}

        for i in range(n_pts):
            res = base_res_tiers[i]
            bx = int(np.floor(xyz[i, 0] / res))
            by = int(np.floor(xyz[i, 1] / res))
            key = (bx, by, res)
            if key not in buckets:
                buckets[key] = []
            buckets[key].append(i)

        cells: Dict[str, Cell25D] = {}
        res_counts = {0.05: 0, 0.10: 0, 0.20: 0, 0.50: 0}
        refined_cell_count = 0

        # Step 2: Process each bucket into a 2.5D cell and evaluate refinement triggers
        # If a bucket requires refinement (steep slope, high roughness, high obstacle risk, high uncertainty),
        # subdivide its points into finer resolution sub-cells.
        for (bx, by, res), indices in buckets.items():
            pts_idx = np.array(indices)
            cell_pts = xyz[pts_idx]
            z_vals = cell_pts[:, 2]
            
            # Dominant semantic class (mode)
            cell_semantics = semantic_labels[pts_idx]
            unique_classes, counts = np.unique(cell_semantics, return_counts=True)
            dom_class = int(unique_classes[np.argmax(counts)])

            # Cell dynamic probability (mean of dynamic points)
            cell_dyn_prob = float(np.mean(dynamic_probs[pts_idx]))
            cell_conf = float(np.mean(confidence_scores[pts_idx]))

            # Preliminary terrain analysis
            terrain_props = self.terrain_analyzer.analyze_cell(
                z_vals, dom_class, cell_dyn_prob, cell_conf, ground_ref_z=ground_ref_z
            )

            # Uncertainty computation
            uncert_props = self.uncertainty_model.compute_cell_uncertainty(
                point_count=len(pts_idx),
                sensor_confidence=cell_conf,
                semantic_confidence=0.85 if dom_class != SemanticClass.UNKNOWN else 0.35,
                terrain_roughness=terrain_props["roughness"],
                dynamic_prob=cell_dyn_prob
            )

            # Traversability calculation
            base_trav = get_traversability_base(dom_class)
            slope_penalty = min(0.9, terrain_props["slope_deg"] / 30.0)
            roughness_penalty = min(0.8, terrain_props["roughness"] / 0.20)
            obs_penalty = min(1.0, terrain_props["obstacle_height"] / 0.50)
            dynamic_penalty = cell_dyn_prob * 0.95
            
            traversability = max(0.0, min(1.0, base_trav * (1.0 - slope_penalty) * (1.0 - roughness_penalty) - obs_penalty - dynamic_penalty))

            # Occupancy: 1 if obstacle or wall, low if clear ground
            if terrain_props["hazard"] in [TerrainHazard.WALL.value, TerrainHazard.OBSTACLE.value]:
                occupancy = 0.95
            elif terrain_props["hazard"] == TerrainHazard.POTHOLE.value:
                occupancy = 0.80
            else:
                occupancy = max(0.05, 1.0 - traversability)

            # Check if cell triggers refinement
            needs_refinement = (
                res > 0.05 and (
                    terrain_props["slope_deg"] >= self.refinement_slope_thresh or
                    terrain_props["roughness"] >= self.refinement_roughness_thresh or
                    uncert_props["uncertainty_score"] >= self.refinement_uncertainty_thresh or
                    terrain_props["hazard"] in [TerrainHazard.POTHOLE.value, TerrainHazard.OBSTACLE.value, TerrainHazard.WALL.value]
                )
            )

            if needs_refinement and len(pts_idx) >= 4:
                # Subdivide into finer resolution!
                target_res = self.refine_resolution(res)
                refined_cell_count += 1
                
                # Sub-bucket points by finer resolution
                sub_buckets: Dict[Tuple[int, int], List[int]] = {}
                for idx in pts_idx:
                    sub_bx = int(np.floor(xyz[idx, 0] / target_res))
                    sub_by = int(np.floor(xyz[idx, 1] / target_res))
                    sub_key = (sub_bx, sub_by)
                    if sub_key not in sub_buckets:
                        sub_buckets[sub_key] = []
                    sub_buckets[sub_key].append(idx)

                for (s_bx, s_by), s_indices in sub_buckets.items():
                    s_idx = np.array(s_indices)
                    s_pts = xyz[s_idx]
                    s_z = s_pts[:, 2]
                    
                    s_semantics = semantic_labels[s_idx]
                    s_unique_classes, s_counts = np.unique(s_semantics, return_counts=True)
                    s_dom_class = int(s_unique_classes[np.argmax(s_counts)])
                    
                    s_dyn = float(np.mean(dynamic_probs[s_idx]))
                    s_conf = float(np.mean(confidence_scores[s_idx]))
                    
                    s_terrain = self.terrain_analyzer.analyze_cell(s_z, s_dom_class, s_dyn, s_conf, ground_ref_z)
                    s_uncert = self.uncertainty_model.compute_cell_uncertainty(
                        len(s_idx), s_conf, 0.90 if s_dom_class != SemanticClass.UNKNOWN else 0.40,
                        s_terrain["roughness"], s_dyn
                    )
                    
                    s_trav = max(0.0, min(1.0, get_traversability_base(s_dom_class) * (1.0 - min(0.9, s_terrain["slope_deg"] / 30.0)) - min(1.0, s_terrain["obstacle_height"] / 0.50) - s_dyn * 0.95))
                    s_occ = 0.95 if s_terrain["hazard"] in [TerrainHazard.WALL.value, TerrainHazard.OBSTACLE.value] else max(0.05, 1.0 - s_trav)

                    # Center coordinate
                    cx = (s_bx + 0.5) * target_res
                    cy = (s_by + 0.5) * target_res
                    cell_id = f"c_{round(cx, 3)}_{round(cy, 3)}_{target_res}"

                    cells[cell_id] = Cell25D(
                        x=round(cx, 3),
                        y=round(cy, 3),
                        resolution=target_res,
                        elevation_mean=s_terrain["elevation_mean"],
                        elevation_min=s_terrain["elevation_min"],
                        elevation_max=s_terrain["elevation_max"],
                        occupancy=round(s_occ, 2),
                        semantic_class=s_dom_class,
                        slope_deg=s_terrain["slope_deg"],
                        roughness=s_terrain["roughness"],
                        traversability=round(s_trav, 2),
                        dynamic_probability=round(s_dyn, 2),
                        confidence=round(s_conf, 2),
                        uncertainty=s_uncert["uncertainty_score"],
                        hazard=s_terrain["hazard"],
                        point_count=len(s_idx),
                        is_refined=True,
                        timestamp=timestamp
                    )
                    res_counts[target_res] += 1
            else:
                # Keep base resolution
                cx = (bx + 0.5) * res
                cy = (by + 0.5) * res
                cell_id = f"c_{round(cx, 3)}_{round(cy, 3)}_{res}"
                
                cells[cell_id] = Cell25D(
                    x=round(cx, 3),
                    y=round(cy, 3),
                    resolution=res,
                    elevation_mean=terrain_props["elevation_mean"],
                    elevation_min=terrain_props["elevation_min"],
                    elevation_max=terrain_props["elevation_max"],
                    occupancy=round(occupancy, 2),
                    semantic_class=dom_class,
                    slope_deg=terrain_props["slope_deg"],
                    roughness=terrain_props["roughness"],
                    traversability=round(traversability, 2),
                    dynamic_probability=round(cell_dyn_prob, 2),
                    confidence=round(cell_conf, 2),
                    uncertainty=uncert_props["uncertainty_score"],
                    hazard=terrain_props["hazard"],
                    point_count=len(pts_idx),
                    is_refined=False,
                    timestamp=timestamp
                )
                res_counts[res] += 1

        t1 = time.perf_counter()
        total_cells = len(cells)
        # Approximate memory: each sparse cell in serialized/in-memory representation is ~48 bytes
        approx_memory_bytes = total_cells * 48

        metrics = {
            "total_cells": total_cells,
            "res_5cm_count": res_counts[0.05],
            "res_10cm_count": res_counts[0.10],
            "res_20cm_count": res_counts[0.20],
            "res_50cm_count": res_counts[0.50],
            "res_5cm_pct": round(res_counts[0.05] / max(1, total_cells) * 100, 1),
            "res_10cm_pct": round(res_counts[0.10] / max(1, total_cells) * 100, 1),
            "res_20cm_pct": round(res_counts[0.20] / max(1, total_cells) * 100, 1),
            "res_50cm_pct": round(res_counts[0.50] / max(1, total_cells) * 100, 1),
            "refined_cells_count": refined_cell_count,
            "processing_time_ms": round((t1 - t0) * 1000.0, 2),
            "memory_bytes": approx_memory_bytes,
            "memory_kb": round(approx_memory_bytes / 1024.0, 2),
            "memory_mb": round(approx_memory_bytes / (1024.0 * 1024.0), 3)
        }
        return cells, metrics
