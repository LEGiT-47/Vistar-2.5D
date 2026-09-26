# VISTAR-2.5D Technical Architecture

## Project Overview
**Problem Statement:** SIH26053 — Adaptive Variable Resolution 2.5D LiDAR Mapping for Dynamic Environment Perception  
**Initiative:** Smart India Hackathon 2026

VISTAR-2.5D converts dense 3D LiDAR point clouds into a lightweight semantic 2.5D terrain representation whose resolution changes automatically according to:
1. Distance foveation (radial proximity to ego vehicle)
2. Terrain complexity (slope gradients, roughness, micro-topography)
3. Object risk (potholes, walls, obstacles, negative elevation defects)
4. Sensor confidence & low-confidence environmental returns (exhaust, smoke, aerosols)
5. Perception uncertainty (point density, temporal stability, DEM elevation difference)

---

## 17-Stage Logical Pipeline

```
Raw 3D LiDAR Point Stream
   │
   ▼ [Stage 1-3]
Range Limiting & Voxel Downsampling
   │
   ▼ [Stage 4]
RANSAC Ground Surface & Obstacle Extraction
   │
   ▼ [Stage 5]
Semantic Segmentation (Harmonized 14-Class Ontology)
   │
   ▼ [Stage 6]
Clear-Vision Low-Confidence Return Filtering (Aerosols / Ghost Returns)
   │
   ▼ [Stage 7]
Terrain Analysis (Slope, Roughness, Elevation Gradients)
   │
   ▼ [Stage 8-9]
Foveated Multi-Scale 2.5D Grid Engine {0.05m, 0.10m, 0.20m, 0.50m}
   │
   ▼ [Stage 10]
Dynamic Actor Segregation (Live Obstacles Kept, Removed from Persistent Terrain)
   │
   ▼ [Stage 11]
Traversability Scoring (SAFE, CAUTION, BLOCKED)
   │
   ▼ [Stage 12]
A* Optimal Hazard-Penalized Route Planning
   │
   ▼ [Stage 13]
Digital Breadcrumb Historical Cache & Deduplication
   │
   ▼ [Stage 14]
Sensor Degradation Resilience & Backtrack Corridor
   │
   ▼ [Stage 15]
Offline DEM Topographic Fusion (Copernicus GLO-90 Outside 40m)
   │
   ▼ [Stage 16]
Rigorous Fixed 5cm vs VISTAR Adaptive Comparison
   │
   ▼ [Stage 17]
Operator Telemetry & Mission Summary Report
```

---

## Adaptive Resolution Rules

Base distance tiers:
- **0 – 10 m:** `0.05 m` (5 cm ultra-high definition near-field)
- **10 – 25 m:** `0.10 m` (10 cm mid-near field)
- **25 – 50 m:** `0.20 m` (20 cm mid-far field)
- **50 – 100 m:** `0.50 m` (50 cm peripheral field)

### Dynamic Refinement Triggers
A cell is automatically refined to `0.10 m` or `0.05 m` if any of the following conditions are met:
- `uncertainty_score > 0.55`
- `slope_deg > 14.0°`
- `surface_roughness > 0.08 m`
- `hazard in [POTHOLE, OBSTACLE, WALL]`

---

## ROS 2 Architecture Abstraction

The system exposes ROS 2 DDS-compatible topics:
- `/vistar/raw_points` (`sensor_msgs/msg/PointCloud2`)
- `/vistar/adaptive_grid` (`vistar_msgs/msg/AdaptiveGrid25D`)
- `/vistar/traversability_map` (`nav_msgs/msg/OccupancyGrid`)
- `/vistar/planned_path` (`nav_msgs/msg/Path`)
- `/vistar/dynamic_obstacles` (`visualization_msgs/msg/MarkerArray`)
- `/vistar/dem_context` (`nav_msgs/msg/OccupancyGrid`)
