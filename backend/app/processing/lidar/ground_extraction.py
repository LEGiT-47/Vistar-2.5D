"""Ground and terrain extraction for VISTAR-2.5D.
Separates drivable ground/terrain points from above-ground obstacles, structures, and canopy.
"""

from typing import Tuple, Dict, Any
import numpy as np

def extract_ground_and_obstacles(
    points: np.ndarray,
    distance_threshold: float = 0.22,
    max_iterations: int = 50,
    expected_ground_z: float = -1.6  # typical sensor mount height above ground
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """Segments points into ground and obstacle points.
    
    Returns:
        ground_mask: boolean array (True for ground)
        ground_points: Nx3 array
        obstacle_points: Mx3 array
        metrics: ground plane coefficients and extraction statistics
    """
    if len(points) == 0:
        empty = np.empty((0, points.shape[1] if points.ndim > 1 else 3))
        return np.zeros(0, dtype=bool), empty, empty, {}

    xyz = points[:, :3]
    num_pts = len(xyz)

    # Initial elevation pre-filter: ground is generally around expected_ground_z ± 1.0m
    rough_ground_candidates = np.where((xyz[:, 2] >= expected_ground_z - 1.2) & (xyz[:, 2] <= expected_ground_z + 0.6))[0]
    
    if len(rough_ground_candidates) < 10:
        # Fallback to bottom 30th percentile
        z_thresh = np.percentile(xyz[:, 2], 30)
        rough_ground_candidates = np.where(xyz[:, 2] <= z_thresh + 0.2)[0]

    # Fast RANSAC plane fitting on candidates
    cand_xyz = xyz[rough_ground_candidates]
    best_inliers_idx = []
    best_plane = np.array([0.0, 0.0, 1.0, -expected_ground_z])

    # Downsample candidates if large for fast RANSAC
    sub_sample_size = min(len(cand_xyz), 1000)
    indices = np.random.choice(len(cand_xyz), sub_sample_size, replace=False)
    sub_xyz = cand_xyz[indices]

    for _ in range(min(max_iterations, 35)):
        sample_idx = np.random.choice(len(sub_xyz), 3, replace=False)
        p1, p2, p3 = sub_xyz[sample_idx]
        
        # Calculate normal vector
        v1 = p2 - p1
        v2 = p3 - p1
        normal = np.cross(v1, v2)
        norm_val = np.linalg.norm(normal)
        if norm_val < 1e-6:
            continue
        normal = normal / norm_val
        
        # Ground plane normal should be mostly vertical (|normal[2]| > 0.8)
        if abs(normal[2]) < 0.75:
            continue
        if normal[2] < 0:
            normal = -normal  # Ensure normal points upwards

        d = -np.dot(normal, p1)
        # Inlier distance check across all rough candidates
        dists = np.abs(np.dot(cand_xyz, normal) + d)
        inliers = np.where(dists < distance_threshold)[0]
        
        if len(inliers) > len(best_inliers_idx):
            best_inliers_idx = inliers
            best_plane = np.append(normal, d)

    # Global ground assignment
    all_dists = np.abs(np.dot(xyz, best_plane[:3]) + best_plane[3])
    # A point is ground if close to fitted plane and not significantly above it
    signed_height = np.dot(xyz, best_plane[:3]) + best_plane[3]
    ground_mask = (all_dists < distance_threshold) & (signed_height < 0.28)

    ground_points = points[ground_mask]
    obstacle_points = points[~ground_mask]

    metrics = {
        "ground_point_count": int(np.sum(ground_mask)),
        "obstacle_point_count": int(num_pts - np.sum(ground_mask)),
        "ground_ratio": round(float(np.sum(ground_mask) / max(1, num_pts)), 3),
        "plane_normal": [round(float(n), 4) for n in best_plane[:3]],
        "plane_offset_d": round(float(best_plane[3]), 4)
    }
    return ground_mask, ground_points, obstacle_points, metrics
