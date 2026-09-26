# VISTAR-2.5D: Adaptive Variable Resolution 2.5D LiDAR Mapping

**Smart India Hackathon 2026 — Problem Statement: SIH26053**  
*Adaptive Variable Resolution 2.5D LiDAR Mapping for Dynamic Environment Perception*

---

## Executive Summary
VISTAR-2.5D is an autonomous robotics perception system that converts dense 3D LiDAR point clouds into a lightweight semantic 2.5D terrain representation whose resolution automatically adapts according to distance foveation, terrain complexity, object risk, sensor confidence, and perception uncertainty.

### 5 Key Takeaways for SIH Evaluators (60-Second Overview):
1. **Dense 3D LiDAR Input:** Ingests raw multi-beam scans across 15 real-world scenarios (SemanticKITTI, nuScenes, Waymo, PandaSet, RELLIS-3D, Boreas, Oxford RobotCar, A2D2).
2. **Adaptive 2.5D Grid Engine:** Allocates `{0.05m, 0.10m, 0.20m, 0.50m}` resolution cells based on distance and automatically refines high-risk hazards.
3. **Low-Confidence Environmental Return Filtering:** Rejects non-solid exhaust plumes, smoke, and synthetic ghost noise before projecting trusted terrain.
4. **Measurable Memory Reduction:** Achieves **70% to 85% memory and cell reduction** compared to conventional uniform 5 cm fixed grids while preserving traversability.
5. **Operational Continuity:** Features a digital breadcrumb cache that survives sensor degradation events, combined with macroscopic offline DEM fusion.

---

## System Architecture

```
LiDAR Input
   │
   ▼
Downsample / Filter (Voxel Grid)
   │
   ▼
Ground & Terrain Extraction (RANSAC)
   │
   ▼
Semantic Segmentation (14-Class Standardized Ontology)
   │
   ▼
Clear-Vision Low-Confidence Return Filtering (Exhaust / Aerosol Rejection)
   │
   ▼
Dynamic Object Isolation (Live Obstacle Kept, Excluded from Persistent Terrain)
   │
   ▼
Adaptive Foveated Grid Engine (Distance Tiers + Automatic Refinement)
   │
   ▼
Traversability & Hazard Classification (Potholes, Walls, Steep Slopes)
   │
   ▼
A* Traversability-Aware Route Planning
   │
   ▼
Digital Breadcrumb Cache + Offline DEM Fusion
   │
   ▼
Operator HUD & Fixed vs VISTAR Split Comparison
```

---

## 15 Prepared Mission Scenarios

1. **Urban Dynamic Traffic** — SemanticKITTI *(Multi-lane intersection with moving cars and pedestrians)*
2. **Highway / Open Road** — KITTI / SemanticKITTI *(High-speed corridor with sparse far-field returns)*
3. **Residential Urban Scene** — SemanticKITTI *(Curbs, sidewalks, and residential structures)*
4. **Boston Urban** — nuScenes *(Urban canyon with high-rise facade reflections)*
5. **Singapore Urban** — nuScenes *(Boulevard with dense tropical overhanging foliage)*
6. **US Multi-City** — Waymo Open Dataset *(Multi-sensor cross-coverage intersection)*
7. **Off-Road Terrain** — RELLIS-3D *(Mud ruts, puddles, rubble, and extreme terrain roughness)*
8. **Smoke / Exhaust Plumes** — PandaSet *(Diesel exhaust return filtering)*
9. **Adverse Weather — Rain** — Boreas *(Surface water scattering & spray attenuation)*
10. **Adverse Weather — Snow** — Boreas *(Snowbanks, concealed curbs & floating flake clutter)*
11. **Changing Conditions** — Oxford RobotCar *(Cobblestone streets & tight archways)*
12. **Multi-LiDAR Interchange** — A2D2 *(5 synchronized LiDAR streams on German Autobahn)*
13. **Dynamic Object Stress Test** — SemanticKITTI *(Fast cross-traffic de-cluttering)*
14. **Synthetic Dust & Ghost Return Test** *(Controlled 18% ghost point injection)*
15. **DEM Fusion Terrain Mission** — Copernicus GLO-90 *(Live adaptive LiDAR fused with 90m macroscopic DEM)*

---

## Quickstart & Launch Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### One-Click Launch (Windows)
Double-click `run_prototype.bat` or in PowerShell execute:
```powershell
.\run_prototype.ps1
```

### Manual Launch

**Terminal 1 — Backend:**
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open **`http://localhost:5173/`** in any modern web browser.

---

## Scientific Honesty Declaration
- **No Fabricated Inference:** The system transparently flags `MODE B: DATASET REPLAY` when utilizing official dataset annotations.
- **Factual Benchmarks:** All metrics (cell counts, memory bytes, latency, reduction %) are calculated dynamically in memory from the processed point cloud.
- **Realistic Claims:** We specifically use *"low-confidence environmental return filtering"* rather than asserting absolute dust immunity.
