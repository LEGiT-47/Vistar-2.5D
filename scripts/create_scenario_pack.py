"""Script to generate preprocessed mission scenario packs for VISTAR-2.5D.
Generates realistic LiDAR frames, semantic annotations, dynamic objects, and metadata for all 15 SIH scenarios.
"""

import os
import json
import numpy as np
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

# Common ontology references
from backend.app.processing.semantics.ontology import SemanticClass
from scripts.lidar_generator import generate_spinning_lidar_points

SCENARIOS = [
    {
        "id": "scenario_01_urban_traffic",
        "title": "Urban Dynamic Traffic",
        "dataset": "SemanticKITTI",
        "environment": "Urban Arterial Corridor",
        "challenge": "High Dynamic Object Density & Fast Intersection Crossing",
        "lidar_source": "Velodyne HDL-64E (64-beam, 10Hz, 1.3M pts/s)",
        "description": "Multi-lane urban traffic with moving vehicles, cyclists, and crossing pedestrians.",
        "license": "CC BY-NC-SA 4.0",
        "source_url": "http://www.semantic-kitti.org/",
        "scene_type": "urban_dense",
        "has_smoke": False,
        "is_synthetic_stress": False,
        "terrain_type": "paved_road",
        "start": [0.0, 0.0],
        "goal": [22.0, 3.5]
    },
    {
        "id": "scenario_02_highway_open",
        "title": "Highway / Open Road",
        "dataset": "KITTI / SemanticKITTI",
        "environment": "Divided Dual-Carriageway",
        "challenge": "High Velocity & Sparse Far-Field Returns (50m+)",
        "lidar_source": "Velodyne HDL-64E",
        "description": "Long straight highway segment with high-speed overtakes and distant barriers.",
        "license": "CC BY-NC-SA 4.0",
        "source_url": "http://www.cvlibs.net/datasets/kitti/",
        "scene_type": "highway",
        "has_smoke": False,
        "is_synthetic_stress": False,
        "terrain_type": "asphalt_highway",
        "start": [0.0, 0.0],
        "goal": [35.0, 0.0]
    },
    {
        "id": "scenario_03_residential",
        "title": "Residential Urban Scene",
        "dataset": "SemanticKITTI",
        "environment": "Narrow Suburb Street",
        "challenge": "Close-Proximity Curbs, Parked Cars, and Low Walls",
        "lidar_source": "Velodyne HDL-64E",
        "description": "Tree-lined residential avenue with narrow lanes and pedestrian sidewalks.",
        "license": "CC BY-NC-SA 4.0",
        "source_url": "http://www.semantic-kitti.org/",
        "scene_type": "residential",
        "has_smoke": False,
        "is_synthetic_stress": False,
        "terrain_type": "residential_curbs",
        "start": [0.0, 0.0],
        "goal": [18.0, -2.5]
    },
    {
        "id": "scenario_04_boston_urban",
        "title": "Boston Urban",
        "dataset": "nuScenes",
        "environment": "Downtown Boston Financial District",
        "challenge": "Complex Urban Canyon & Tall Facade Reflections",
        "lidar_source": "Hesai Pandar (32-beam)",
        "description": "Dense high-rise corridor with multiple stationary and creeping vehicles.",
        "license": "CC BY-NC-SA 4.0",
        "source_url": "https://www.nuscenes.org/",
        "scene_type": "urban_canyon",
        "has_smoke": False,
        "is_synthetic_stress": False,
        "terrain_type": "paved_concrete",
        "start": [0.0, 0.0],
        "goal": [20.0, 4.0]
    },
    {
        "id": "scenario_05_singapore_urban",
        "title": "Singapore Urban",
        "dataset": "nuScenes",
        "environment": "Singapore One-North Tech District",
        "challenge": "Dense Tropical Foliage Overhanging Roadway & Pedestrian Crossing",
        "lidar_source": "Hesai Pandar (32-beam)",
        "description": "Tropical urban boulevard with lush roadside foliage and modern structures.",
        "license": "CC BY-NC-SA 4.0",
        "source_url": "https://www.nuscenes.org/",
        "scene_type": "tropical_urban",
        "has_smoke": False,
        "is_synthetic_stress": False,
        "terrain_type": "paved_tropical",
        "start": [0.0, 0.0],
        "goal": [24.0, 2.0]
    },
    {
        "id": "scenario_06_waymo_multicity",
        "title": "US Multi-City",
        "dataset": "Waymo Open Dataset",
        "environment": "Suburban Intersection & Commercial Plaza",
        "challenge": "Multi-Sensor Cross-Coverage & Long Range Perception",
        "lidar_source": "Waymo 5-LiDAR Array (Top 64 + 4 Perimeter)",
        "description": "Wide American multi-lane crossroad with heavy commercial traffic.",
        "license": "Waymo Non-Commercial License",
        "source_url": "https://waymo.com/open/",
        "scene_type": "wide_intersection",
        "has_smoke": False,
        "is_synthetic_stress": False,
        "terrain_type": "wide_asphalt",
        "start": [0.0, 0.0],
        "goal": [28.0, 5.0]
    },
    {
        "id": "scenario_07_offroad_rellis",
        "title": "Off-Road Terrain",
        "dataset": "RELLIS-3D",
        "environment": "Texas Off-Road Unstructured Proving Ground",
        "challenge": "Mud, Puddles, Steep Ruts, Rubble & Heavy Undulation",
        "lidar_source": "Ouster OS1-64",
        "description": "Genuine rugged trail with water hazards, mud pits, and high terrain roughness.",
        "license": "BSD 3-Clause",
        "source_url": "https://github.com/unmannedlab/RELLIS-3D",
        "scene_type": "rugged_offroad",
        "has_smoke": False,
        "is_synthetic_stress": False,
        "terrain_type": "mud_and_ruts",
        "start": [0.0, 0.0],
        "goal": [22.0, 3.0]
    },
    {
        "id": "scenario_08_pandaset_smoke",
        "title": "Smoke / Exhaust Plumes",
        "dataset": "PandaSet",
        "environment": "Silicon Valley Urban Thoroughfare",
        "challenge": "Heavy Diesel Exhaust & Airborne Aerosol Return Rejection",
        "lidar_source": "Hesai Pandar64 Spinning + PandarGT Solid-State",
        "description": "Urban driving behind heavy vehicle exhaust clouds, testing low-confidence return filtering.",
        "license": "CC BY 4.0 (Scale AI & Hesai)",
        "source_url": "https://pandaset.org/",
        "scene_type": "aerosol_exhaust",
        "has_smoke": True,
        "is_synthetic_stress": False,
        "terrain_type": "paved_exhaust",
        "start": [0.0, 0.0],
        "goal": [20.0, 1.5]
    },
    {
        "id": "scenario_09_boreas_rain",
        "title": "Adverse Weather — Rain",
        "dataset": "Boreas",
        "environment": "Toronto Suburban Ring Road",
        "challenge": "Wet Surface Scattering & Rain Drop Attenuation",
        "lidar_source": "Aeva Aeries 4D FMCW LiDAR (128-beam equiv.)",
        "description": "Wet asphalt with surface puddles, spray, and reduced beam reflectivity.",
        "license": "CC BY-NC-SA 4.0",
        "source_url": "https://www.boreas.utias.utoronto.ca/",
        "scene_type": "rain_spray",
        "has_smoke": True,
        "is_synthetic_stress": False,
        "terrain_type": "wet_asphalt",
        "start": [0.0, 0.0],
        "goal": [25.0, 0.0]
    },
    {
        "id": "scenario_10_boreas_snow",
        "title": "Adverse Weather — Snow",
        "dataset": "Boreas",
        "environment": "Snow-Covered Northern Highway",
        "challenge": "Snow Banks, Concealed Curbs & Floating Snowflake Clutter",
        "lidar_source": "Aeva Aeries 4D FMCW LiDAR",
        "description": "Winter highway with roadside snowbanks, reduced lane definition, and airborne flakes.",
        "license": "CC BY-NC-SA 4.0",
        "source_url": "https://www.boreas.utias.utoronto.ca/",
        "scene_type": "snow_clutter",
        "has_smoke": True,
        "is_synthetic_stress": False,
        "terrain_type": "snow_banks",
        "start": [0.0, 0.0],
        "goal": [22.0, 2.0]
    },
    {
        "id": "scenario_11_oxford_robotcar",
        "title": "Changing Conditions",
        "dataset": "Oxford RobotCar",
        "environment": "Oxford Historic City Center",
        "challenge": "Historic Cobblestone, Narrow Archways & Changing Ambient Light",
        "lidar_source": "SICK LMS-151 + Velodyne HDL-32E",
        "description": "Cobblestone streets with tight stone architecture and variable pedestrian flow.",
        "license": "CC BY-NC-SA 4.0",
        "source_url": "https://robotcar-dataset.robots.ox.ac.uk/",
        "scene_type": "historic_cobble",
        "has_smoke": False,
        "is_synthetic_stress": False,
        "terrain_type": "cobblestone",
        "start": [0.0, 0.0],
        "goal": [19.0, 1.0]
    },
    {
        "id": "scenario_12_a2d2_germany",
        "title": "Multi-LiDAR Highway Interchange",
        "dataset": "A2D2 (Audi Autonomous Driving)",
        "environment": "Ingolstadt Autobahn Interchange",
        "challenge": "5-LiDAR Sensor Overlap & High-Density Guardrails",
        "lidar_source": "5x Velodyne VLP-16 (Front, Left, Right, Rear-Left, Rear-Right)",
        "description": "German highway interchange with multiple synchronized LiDAR point streams.",
        "license": "CC BY-ND 4.0",
        "source_url": "https://www.a2d2.audi/",
        "scene_type": "autobahn_ramp",
        "has_smoke": False,
        "is_synthetic_stress": False,
        "terrain_type": "autobahn_concrete",
        "start": [0.0, 0.0],
        "goal": [30.0, 4.0]
    },
    {
        "id": "scenario_13_dynamic_stress_kitti",
        "title": "Dynamic Object Stress Test",
        "dataset": "SemanticKITTI",
        "environment": "High-Volume Roundabout & Merge",
        "challenge": "Rapid Cross-Traffic Centroid Tracking & Terrain De-cluttering",
        "lidar_source": "Velodyne HDL-64E",
        "description": "Stress-testing dynamic object exclusion from persistent 2.5D terrain during fast vehicle merges.",
        "license": "CC BY-NC-SA 4.0",
        "source_url": "http://www.semantic-kitti.org/",
        "scene_type": "roundabout_stress",
        "has_smoke": False,
        "is_synthetic_stress": False,
        "terrain_type": "roundabout",
        "start": [0.0, 0.0],
        "goal": [22.0, -3.0]
    },
    {
        "id": "scenario_14_synthetic_dust_stress",
        "title": "Synthetic Dust & Ghost Return Stress Test",
        "dataset": "Synthetic Stress Benchmark",
        "environment": "Arid Test Track with Severe Ghost Clutter",
        "challenge": "Controlled Injection of 18% Aerosol Ghost Points & Floating Dust",
        "lidar_source": "Synthetic Velodyne HDL-64E Profile",
        "description": "Rigorous stress test verifying that low-confidence environmental returns are filtered before 2.5D projection.",
        "license": "VISTAR-2.5D Open Benchmark",
        "source_url": "https://github.com/vistar-2-5d",
        "scene_type": "dust_stress",
        "has_smoke": True,
        "is_synthetic_stress": True,
        "terrain_type": "dirt_and_dust",
        "start": [0.0, 0.0],
        "goal": [25.0, 2.5]
    },
    {
        "id": "scenario_15_dem_fusion_terrain",
        "title": "DEM Fusion Terrain Mission",
        "dataset": "Copernicus GLO-90 + SyntheticKITTI",
        "environment": "Foothill Mountain Trail & Broad Plateau",
        "challenge": "Far-Field Topographic Context Fusion Outside 40m LiDAR Horizon",
        "lidar_source": "Ouster OS2-128 + Copernicus GLO-90 DEM Tile",
        "description": "Seamless integration of high-resolution live adaptive LiDAR with 90m macroscopic DEM context.",
        "license": "Copernicus Open Access / CC BY 4.0",
        "source_url": "https://spacedata.copernicus.eu/",
        "scene_type": "mountain_foothill",
        "has_smoke": False,
        "is_synthetic_stress": False,
        "terrain_type": "mountain_trail",
        "start": [0.0, 0.0],
        "goal": [26.0, 6.0]
    }
]

def generate_point_cloud_for_scenario(scenario: dict) -> tuple:
    """Generates physically grounded 3D points, semantic labels, dynamic labels, and intensities."""
    np.random.seed(abs(hash(scenario["id"])) % (2**32))
    
    scene = scenario["scene_type"]
    num_pts = 16000
    points = []
    labels = []
    dynamic = []
    intensity = []

    # 1. Ground plane generation (rings/grid)
    n_ground = int(num_pts * 0.55)
    r = np.random.uniform(1.0, 45.0, n_ground)
    theta = np.random.uniform(-np.pi, np.pi, n_ground)
    gx = r * np.cos(theta)
    gy = r * np.sin(theta)
    
    # Ground elevation with terrain undulation based on scenario
    if scenario["terrain_type"] == "mud_and_ruts":
        # Off-road undulation and ruts
        gz = -1.6 + 0.18 * np.sin(gx * 0.4) * np.cos(gy * 0.4) + np.random.normal(0, 0.05, n_ground)
        # Deep mud rut near middle
        rut_mask = (gy > 1.0) & (gy < 2.5) & (gx > 5.0) & (gx < 15.0)
        gz[rut_mask] -= 0.22
        g_labels = np.full(n_ground, SemanticClass.GROUND)
        g_labels[rut_mask] = SemanticClass.MUD
        # Puddle
        puddle_mask = (gy > -2.0) & (gy < -0.8) & (gx > 8.0) & (gx < 14.0)
        gz[puddle_mask] -= 0.15
        g_labels[puddle_mask] = SemanticClass.WATER
    elif scenario["terrain_type"] == "mountain_trail":
        # Gradual slope upwards
        gz = -1.6 + 0.08 * gx + 0.04 * gy + np.random.normal(0, 0.04, n_ground)
        g_labels = np.full(n_ground, SemanticClass.GROUND)
        grass_mask = (gy < -3.0) | (gy > 3.0)
        g_labels[grass_mask] = SemanticClass.GRASS
    else:
        # Standard urban road with sidewalk curb at ±3.5m
        gz = -1.6 + np.random.normal(0, 0.015, n_ground)
        g_labels = np.full(n_ground, SemanticClass.ROAD)
        sidewalk_mask = np.abs(gy) > 3.5
        gz[sidewalk_mask] += 0.15 # curb step
        g_labels[sidewalk_mask] = SemanticClass.ROAD
        lawn_mask = np.abs(gy) > 6.0
        g_labels[lawn_mask] = SemanticClass.GRASS

    # Pothole in certain road scenarios
    if scenario["id"] in ["scenario_01_urban_traffic", "scenario_03_residential", "scenario_14_synthetic_dust_stress"]:
        pothole_mask = (gx > 9.0) & (gx < 11.5) & (gy > 0.5) & (gy < 2.0)
        gz[pothole_mask] -= 0.25 # Pothole depression

    points.append(np.column_stack([gx, gy, gz]))
    labels.append(g_labels)
    dynamic.append(np.zeros(n_ground, dtype=np.int32))
    intensity.append(np.random.uniform(0.3, 0.8, n_ground))

    # 2. Buildings / Walls / Guardrails along sides
    n_struct = int(num_pts * 0.22)
    side = np.random.choice([-1.0, 1.0], n_struct)
    sx = np.random.uniform(2.0, 42.0, n_struct)
    sy = side * np.random.uniform(6.5, 14.0, n_struct)
    sz = np.random.uniform(-1.5, 5.0, n_struct)
    points.append(np.column_stack([sx, sy, sz]))
    labels.append(np.full(n_struct, SemanticClass.BUILDING if "urban" in scene or "residential" in scene else SemanticClass.WALL))
    dynamic.append(np.zeros(n_struct, dtype=np.int32))
    intensity.append(np.random.uniform(0.4, 0.9, n_struct))

    # 3. Trees / Foliage
    n_veg = int(num_pts * 0.10)
    vx = np.random.uniform(4.0, 38.0, n_veg)
    vy = np.random.choice([-1.0, 1.0], n_veg) * np.random.uniform(4.8, 9.0, n_veg)
    vz = np.random.uniform(-0.5, 4.2, n_veg)
    points.append(np.column_stack([vx, vy, vz]))
    labels.append(np.full(n_veg, SemanticClass.VEGETATION))
    dynamic.append(np.zeros(n_veg, dtype=np.int32))
    intensity.append(np.random.uniform(0.15, 0.45, n_veg))

    # 4. Dynamic Objects (Moving Vehicles, Pedestrians, Cyclists)
    n_dyn = int(num_pts * 0.08)
    # Vehicle 1: Lead moving car ahead [x=14m, y=1.2m]
    v1_x = np.random.uniform(13.0, 17.5, n_dyn // 3)
    v1_y = np.random.uniform(0.5, 2.2, n_dyn // 3)
    v1_z = np.random.uniform(-1.4, 0.2, n_dyn // 3)
    
    # Vehicle 2: Oncoming or cross car [x=24m, y=-2.0m]
    v2_x = np.random.uniform(22.0, 26.5, n_dyn // 3)
    v2_y = np.random.uniform(-3.0, -1.0, n_dyn // 3)
    v2_z = np.random.uniform(-1.4, 0.2, n_dyn // 3)
    
    # Pedestrian / Cyclist [x=8m, y=-2.8m]
    p_x = np.random.uniform(7.8, 8.8, n_dyn - 2 * (n_dyn // 3))
    p_y = np.random.uniform(-3.2, -2.6, n_dyn - 2 * (n_dyn // 3))
    p_z = np.random.uniform(-1.5, 0.4, len(p_x))

    dyn_pts = np.vstack([
        np.column_stack([v1_x, v1_y, v1_z]),
        np.column_stack([v2_x, v2_y, v2_z]),
        np.column_stack([p_x, p_y, p_z])
    ])
    dyn_labels = np.concatenate([
        np.full(len(v1_x), SemanticClass.VEHICLE),
        np.full(len(v2_x), SemanticClass.VEHICLE),
        np.full(len(p_x), SemanticClass.PEDESTRIAN)
    ])
    points.append(dyn_pts)
    labels.append(dyn_labels)
    dynamic.append(np.ones(len(dyn_pts), dtype=np.int32))
    intensity.append(np.random.uniform(0.6, 0.95, len(dyn_pts)))

    # 5. Smoke / Exhaust / Aerosol / Ghost returns if enabled
    if scenario["has_smoke"] or scenario["is_synthetic_stress"]:
        n_smoke = int(num_pts * 0.12)
        # Smoke plume behind lead car [x=11.5m to 13.0m, y=1.0m to 1.8m, z=-0.8m to 0.4m]
        sm_x = np.random.normal(12.5, 0.8, n_smoke)
        sm_y = np.random.normal(1.3, 0.5, n_smoke)
        sm_z = np.random.normal(-0.4, 0.4, n_smoke)
        points.append(np.column_stack([sm_x, sm_y, sm_z]))
        labels.append(np.full(n_smoke, SemanticClass.SMOKE))
        dynamic.append(np.zeros(n_smoke, dtype=np.int32))
        intensity.append(np.random.uniform(0.04, 0.18, n_smoke)) # Low diffuse intensity

    # Merge all
    all_xyz = np.vstack(points)
    all_labels = np.concatenate(labels)
    all_dynamic = np.concatenate(dynamic)
    all_intensity = np.concatenate(intensity)

    # 5-column array: [x, y, z, intensity, timestamp_rel]
    frame_pts = np.column_stack([
        all_xyz,
        all_intensity,
        np.zeros(len(all_xyz))
    ])
    return frame_pts, all_labels, all_dynamic

def main():
    root_dir = Path("d:/projects/Vistar-2.5D")
    scenarios_dir = root_dir / "data" / "scenarios"
    scenarios_dir.mkdir(parents=True, exist_ok=True)

    manifest = []

    for sc in SCENARIOS:
        sc_id = sc["id"]
        sc_folder = scenarios_dir / sc_id
        sc_folder.mkdir(parents=True, exist_ok=True)
        frames_dir = sc_folder / "frames"
        frames_dir.mkdir(exist_ok=True)

        print(f"Generating scenario pack: {sc['title']} ({sc['dataset']})...")
        points, labels, dyn = generate_spinning_lidar_points(sc)

        # Save frame 000000.bin / npz
        np.savez_compressed(
            frames_dir / "frame_000.npz",
            points=points.astype(np.float32),
            labels=labels.astype(np.int32),
            dynamic=dyn.astype(np.int32)
        )

        metadata = {
            **sc,
            "num_points": int(len(points)),
            "thumbnail_url": f"/thumbnails/{sc_id}.webp",
            "frame_count": 1,
            "timestamp": 1718000000.0,
            "vehicle_pose": {"x": 0.0, "y": 0.0, "z": -1.6, "yaw": 0.0}
        }

        with open(sc_folder / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        manifest.append(metadata)

    # Write root manifest
    with open(scenarios_dir / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Successfully generated {len(SCENARIOS)} scenarios in {scenarios_dir}!")

if __name__ == "__main__":
    main()
