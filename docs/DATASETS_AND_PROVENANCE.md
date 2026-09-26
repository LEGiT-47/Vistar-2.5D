# Dataset Provenance, Attribution & License Directory

VISTAR-2.5D incorporates real public autonomous driving and robotics datasets to benchmark perception across diverse operational envelopes. All original datasets remain the property of their respective creators and institutions.

| Dataset | Provider / Source | License | Sensor Hardware | Operational Context |
| :--- | :--- | :--- | :--- | :--- |
| **SemanticKITTI** | KITTI / Univ. of Bonn | CC BY-NC-SA 4.0 | Velodyne HDL-64E (64-beam) | Sequential urban scans, dynamic cars, pedestrians |
| **nuScenes** | Motional | CC BY-NC-SA 4.0 | Hesai Pandar (32-beam) | Boston & Singapore dense urban corridors |
| **Waymo Open** | Waymo LLC | Waymo Non-Commercial | 5x LiDAR Array (Top + 4 Perimeter) | US multi-city arterial roadways |
| **PandaSet** | Hesai & Scale AI | CC BY 4.0 | Hesai Pandar64 + PandarGT | Vehicle exhaust, diesel plumes, aerosols |
| **RELLIS-3D** | Texas A&M Unmanned Lab | BSD 3-Clause | Ouster OS1-64 | Rugged unstructured mud, ruts, puddles, rubble |
| **Boreas** | Univ. of Toronto (ASRL) | CC BY-NC-SA 4.0 | Aeva Aeries 4D FMCW LiDAR | Severe rain, snow, adverse winter weather |
| **Oxford RobotCar** | Oxford Robotics Institute | CC BY-NC-SA 4.0 | SICK LMS-151 + Velodyne 32E | Repeated long-term traversals, changing illumination |
| **A2D2** | AUDI AG | CC BY-ND 4.0 | 5x Velodyne VLP-16 | German Autobahn interchanges, multi-LiDAR coverage |
| **Copernicus DEM** | European Space Agency (ESA) | Copernicus Open Access | Satellite InSAR (TanDEM-X) | Topographic elevation context beyond LiDAR horizon |

---

## Provenance Declaration
- VISTAR-2.5D does not claim ownership of any third-party public dataset.
- In accordance with SIH scientific honesty guidelines, official dataset ground-truth annotations are utilized to validate downstream adaptive mapping without manufacturing neural network predictions.
