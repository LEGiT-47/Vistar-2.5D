"""VISTAR-2.5D Complete Pipeline Coordinator.
Implements the 17-stage perception and mapping sequence, streaming events and machine-readable statistics.
"""

import time
from typing import Dict, Any, List, Optional
import numpy as np

from .lidar.filters import filter_point_cloud
from .lidar.ground_extraction import extract_ground_and_obstacles
from .semantics.ontology import SemanticClass
from .semantics.inference import SemanticSegmentationEngine
from .dynamic.dynamic_detector import DynamicObjectDetector
from .low_confidence.clear_vision import ClearVisionFilter
from .terrain.terrain_analyzer import TerrainAnalyzer
from .uncertainty.uncertainty_model import UncertaintyModel
from .adaptive_grid.foveated_grid import AdaptiveFoveatedGridEngine
from .adaptive_grid.fixed_baseline import compute_fixed_baseline_grid, compare_fixed_vs_vistar
from .planning.route_planner import RoutePlanner
from .cache.breadcrumb_cache import BreadcrumbCacheEngine
from .dem.dem_fusion import DEMFusionEngine

class VistarPipeline:
    def __init__(self):
        self.semantic_engine = SemanticSegmentationEngine()
        self.dynamic_detector = DynamicObjectDetector()
        self.clear_vision_filter = ClearVisionFilter()
        self.adaptive_grid_engine = AdaptiveFoveatedGridEngine()
        self.route_planner = RoutePlanner()
        self.cache_engine = BreadcrumbCacheEngine()
        self.dem_fusion_engine = DEMFusionEngine()
        self.uncertainty_model = UncertaintyModel()

    def run_full_pipeline(
        self,
        raw_points: np.ndarray,
        ground_truth_labels: Optional[np.ndarray] = None,
        instance_ids: Optional[np.ndarray] = None,
        dynamic_labels: Optional[np.ndarray] = None,
        is_synthetic_stress: bool = False,
        start_point: Optional[List[float]] = None,
        goal_point: Optional[List[float]] = None,
        ego_pose: Optional[Dict[str, float]] = None,
        timestamp: float = 0.0
    ) -> Dict[str, Any]:
        """Runs all stages of the pipeline and produces complete telemetry and visualization payloads."""
        t_start = time.perf_counter()
        results: Dict[str, Any] = {}

        # Stage 1: LiDAR Input
        raw_count = len(raw_points)
        results["stage_1_input"] = {
            "raw_point_count": raw_count,
            "has_intensity": raw_points.shape[1] > 3 if raw_points.ndim > 1 else False,
            "timestamp": timestamp
        }

        # Stage 2 & 3: Downsample / Filter
        filtered_points, filter_stats = filter_point_cloud(raw_points, voxel_size=0.06)
        results["stage_2_filter"] = filter_stats

        # Stage 4: Ground & Terrain Extraction
        ground_mask, ground_pts, obstacle_pts, ground_stats = extract_ground_and_obstacles(filtered_points)
        results["stage_3_ground"] = ground_stats

        # Stage 5: Semantic Segmentation (Transparent Mode A vs Mode B)
        # Match or resample labels to filtered points
        if ground_truth_labels is not None and len(ground_truth_labels) == raw_count:
            # Subsample labels if filtered
            pts_labels = ground_truth_labels[:len(filtered_points)]
        else:
            pts_labels = None

        semantic_labels, sem_stats = self.semantic_engine.predict(filtered_points, pts_labels)
        results["stage_4_semantics"] = sem_stats

        # Stage 6: Low-Confidence Environmental Return Filter
        intensity = filtered_points[:, 3] if filtered_points.shape[1] > 3 else None
        confidence_scores, trusted_mask, trusted_points, cv_stats = self.clear_vision_filter.filter_returns(
            filtered_points, semantic_labels, intensity, synthetic_stress_test=is_synthetic_stress
        )
        results["stage_5_clear_vision"] = cv_stats

        # Use trusted subset for terrain projection
        trusted_semantics = semantic_labels[trusted_mask]

        # Stage 7: Dynamic Object Detection
        dyn_probs, is_dyn_mask, dyn_stats = self.dynamic_detector.analyze_dynamics(
            trusted_points, trusted_semantics, timestamp=timestamp
        )
        results["stage_6_dynamic"] = dyn_stats

        # Dynamic actors separated: kept visible as live obstacles, excluded from persistent terrain
        live_dynamic_points = trusted_points[is_dyn_mask]
        static_terrain_points = trusted_points[~is_dyn_mask]
        static_semantics = trusted_semantics[~is_dyn_mask]
        static_dyn_probs = dyn_probs[~is_dyn_mask]
        static_conf = confidence_scores[trusted_mask][~is_dyn_mask]

        # Stage 8 & 9: Adaptive Foveated Grid Engine
        adaptive_cells, adaptive_stats = self.adaptive_grid_engine.build_adaptive_grid(
            static_terrain_points, static_semantics, static_dyn_probs, static_conf, timestamp=timestamp
        )
        results["stage_7_adaptive_grid"] = adaptive_stats

        # Stage 10: Fixed 5 cm Baseline Comparison (Mandatory)
        fixed_stats = compute_fixed_baseline_grid(static_terrain_points, fixed_res=0.05)
        comparison_stats = compare_fixed_vs_vistar(fixed_stats, adaptive_stats)
        results["stage_8_comparison"] = comparison_stats

        # Stage 11: Route Planning (A*)
        start_xy = (start_point[0], start_point[1]) if start_point else (0.0, 0.0)
        goal_xy = (goal_point[0], goal_point[1]) if goal_point else (18.0, 4.0)
        plan_results = self.route_planner.plan_path(adaptive_cells, start_xy, goal_xy)
        results["stage_9_planning"] = plan_results

        # Stage 12: Historical Breadcrumb Cache
        cache_stats = self.cache_engine.update_cache(
            adaptive_cells, ego_pose or {"x": start_xy[0], "y": start_xy[1], "z": -1.6}, raw_count, timestamp
        )
        results["stage_10_cache"] = cache_stats

        # Stage 13: Offline DEM Integration & Agreement
        dem_cells, dem_stats = self.dem_fusion_engine.fuse_dem_context(adaptive_cells)
        results["stage_11_dem"] = dem_stats

        # Stage 14: Overall Trust Score Calculation
        overall_trust = self.uncertainty_model.compute_mission_trust_score(
            avg_density=filter_stats.get("estimated_density_pts_m2", 15.0),
            low_confidence_ratio=cv_stats.get("rejection_percentage", 0.0) / 100.0,
            dem_agreement_score=dem_stats.get("dem_agreement_score", 85.0),
            dynamic_ratio=dyn_stats.get("dynamic_ratio", 0.05)
        )
        results["mission_trust_score"] = overall_trust

        t_total = time.perf_counter() - t_start
        results["total_pipeline_time_ms"] = round(t_total * 1000.0, 2)

        # Prepare compressed visualization arrays for Three.js
        # Downsample point cloud for 60fps web rendering (max 20,000 points per frame)
        vis_stride = max(1, len(filtered_points) // 18000)
        vis_pts = filtered_points[::vis_stride]
        vis_sem = semantic_labels[::vis_stride]
        vis_conf = confidence_scores[::vis_stride]

        # Flatten points for Three.js Float32BufferAttribute
        results["vis_payload"] = {
            "points": vis_pts[:, :3].flatten().tolist(),
            "semantics": vis_sem.tolist(),
            "confidence": [round(float(c), 2) for c in vis_conf],
            "dynamic_points": live_dynamic_points[::2, :3].flatten().tolist() if len(live_dynamic_points) > 0 else [],
            "cells": [c.to_dict() for c in list(adaptive_cells.values())[:3000]], # Active cells
            "dem_cells": dem_cells[:800],
            "route_waypoints": plan_results["waypoints"],
            "trajectory": self.cache_engine.trajectory_poses[-50:],
            "start": list(start_xy),
            "goal": list(goal_xy)
        }

        return results
