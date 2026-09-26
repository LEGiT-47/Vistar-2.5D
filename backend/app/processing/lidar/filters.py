"""LiDAR preprocessing, range limiting, voxel downsampling, and geometric features.
"""

import time
from typing import Dict, Any, Tuple
import numpy as np

def filter_point_cloud(
    points: np.ndarray,
    min_range: float = 0.5,
    max_range: float = 75.0,
    voxel_size: float = 0.05,
    min_z: float = -5.0,
    max_z: float = 15.0,
    return_indices: bool = False
) -> Tuple[np.ndarray, Dict[str, Any]] | Tuple[np.ndarray, Dict[str, Any], np.ndarray]:
    """Applies valid range limits, bounding box, and voxel downsampling.
    
    Args:
        points: Nx(3..5) array [x, y, z, intensity?, ...]
        min_range: minimum Euclidean distance from ego sensor
        max_range: maximum LiDAR range
        voxel_size: grid quantization size for downsampling
    
    Returns:
        filtered_points: Mx(3..5) array
        stats: dictionary with timing, counts, density
    """
    t0 = time.perf_counter()
    raw_count = len(points)
    if raw_count == 0:
        result = (points, {"raw_count": 0, "filtered_count": 0, "removed_count": 0, "time_ms": 0.0})
        return (*result, np.empty(0, dtype=np.int64)) if return_indices else result

    # 1. Coordinate check and range filtering
    xyz = points[:, :3]
    dists = np.linalg.norm(xyz[:, :2], axis=1) # XY range
    valid_mask = (
        np.isfinite(xyz).all(axis=1) &
        (dists >= min_range) &
        (dists <= max_range) &
        (xyz[:, 2] >= min_z) &
        (xyz[:, 2] <= max_z)
    )
    ranged_indices = np.flatnonzero(valid_mask)
    pts_ranged = points[ranged_indices]

    # 2. Voxel grid downsampling (fast NumPy hashing)
    if voxel_size > 0 and len(pts_ranged) > 0:
        voxel_coords = np.floor(pts_ranged[:, :3] / voxel_size).astype(np.int64)
        # Use structured array or unique indices
        _, unique_indices = np.unique(voxel_coords, axis=0, return_index=True)
        filtered_points = pts_ranged[unique_indices]
        filtered_indices = ranged_indices[unique_indices]
    else:
        filtered_points = pts_ranged
        filtered_indices = ranged_indices

    t1 = time.perf_counter()
    dt_ms = (t1 - t0) * 1000.0
    filtered_count = len(filtered_points)
    removed_count = raw_count - filtered_count

    # Density estimation (points / effective XY area)
    if filtered_count > 0:
        xy_radius = np.max(np.linalg.norm(filtered_points[:, :2], axis=1))
        approx_area = np.pi * max(1.0, xy_radius**2)
        density = filtered_count / approx_area
    else:
        density = 0.0

    stats = {
        "raw_point_count": int(raw_count),
        "filtered_point_count": int(filtered_count),
        "removed_point_count": int(removed_count),
        "filter_time_ms": round(dt_ms, 2),
        "estimated_density_pts_m2": round(float(density), 2),
        "effective_range_m": round(float(np.max(dists[valid_mask])) if np.any(valid_mask) else 0.0, 2)
    }
    return (filtered_points, stats, filtered_indices) if return_indices else (filtered_points, stats)

def compute_point_cloud_metrics(points: np.ndarray) -> Dict[str, float]:
    """Compute local elevation variation and spatial roughness."""
    if len(points) == 0:
        return {"mean_z": 0.0, "std_z": 0.0, "min_z": 0.0, "max_z": 0.0}
    z = points[:, 2]
    return {
        "mean_z": float(np.mean(z)),
        "std_z": float(np.std(z)),
        "min_z": float(np.min(z)),
        "max_z": float(np.max(z)),
        "height_variation": float(np.max(z) - np.min(z))
    }
