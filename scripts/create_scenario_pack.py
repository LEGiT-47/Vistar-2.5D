"""Script to generate preprocessed mission scenario packs for VISTAR-2.5D.
Generates realistic LiDAR frames, semantic annotations, dynamic objects, and metadata for all 15 SIH scenarios.
"""

import os
import json
import zlib
import numpy as np
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

# Common ontology references
from backend.app.processing.semantics.ontology import SemanticClass

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
        "point_budget": 28000,
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
        "point_budget": 9000,
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
        "point_budget": 6500,
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
        "point_budget": 18000,
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
        "point_budget": 16000,
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
        "point_budget": 22000,
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
        "point_budget": 12500,
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
        "point_budget": 10000,
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
        "point_budget": 7000,
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
        "point_budget": 5500,
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
        "point_budget": 4500,
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
        "point_budget": 14500,
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
        "point_budget": 26000,
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
        "point_budget": 12000,
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
        "goal": [26.0, 6.0],
        "point_budget": 8000
    },
    {
        "id": "scenario_16_lightweight_campus",
        "title": "Lightweight Campus Scout",
        "dataset": "VISTAR Compact Replay",
        "environment": "Pedestrian Campus Service Lane",
        "challenge": "Fast Interactive Mapping with a Compact LiDAR Return Set",
        "lidar_source": "Compact 16-beam LiDAR profile",
        "description": "A deliberately lightweight campus route with sparse returns for low-latency operator replay.",
        "license": "VISTAR-2.5D Open Benchmark",
        "source_url": "https://github.com/vistar-2-5d",
        "scene_type": "campus_lightweight",
        "has_smoke": False,
        "is_synthetic_stress": False,
        "terrain_type": "paved_campus",
        "point_budget": 2400,
        "start": [0.0, 0.0],
        "goal": [16.0, 1.5]
    }
]

SCENE_SIGNATURES = {
    "urban_dense": "Dense arterial: facade blocks + crossing traffic",
    "highway": "Open highway: twin guardrails + long vehicle corridor",
    "residential": "Residential street: detached houses + parked-car pockets",
    "urban_canyon": "Urban canyon: tall towers + narrow street view",
    "tropical_urban": "Tropical boulevard: canopy clusters + central divider",
    "wide_intersection": "Four-way junction: signal poles + cross traffic",
    "rugged_offroad": "Rugged trail: mud ruts + boulders + puddles",
    "aerosol_exhaust": "Exhaust scene: truck corridor + aerosol plume",
    "rain_spray": "Rain corridor: wet road + raised barriers + spray",
    "snow_clutter": "Snow highway: snowbanks + roadside clutter",
    "historic_cobble": "Historic lane: low stone walls + cobblestones",
    "autobahn_ramp": "Interchange ramp: parallel barriers + merge traffic",
    "roundabout_stress": "Roundabout: circular island + radial traffic",
    "dust_stress": "Dust track: scattered rocks + ghost returns",
    "mountain_foothill": "Mountain trail: rising slope + rock outcrops",
    "campus_lightweight": "Campus scout: compact trees + pedestrian furniture",
}

def generate_point_cloud_for_scenario(scenario: dict) -> tuple:
    """Generates physically grounded 3D points, semantic labels, dynamic labels, and intensities."""
    np.random.seed(zlib.crc32(scenario["id"].encode("utf-8")))
    
    scene = scenario["scene_type"]
    num_pts = int(scenario.get("point_budget", 16000))
    points = []
    labels = []
    dynamic = []
    intensity = []

    profile = {
        "urban_dense": (34.0, "radial", 0.16, 0.08, 0.14),
        "highway": (48.0, "corridor", 0.10, 0.04, 0.05),
        "residential": (28.0, "street", 0.12, 0.16, 0.04),
        "urban_canyon": (30.0, "canyon", 0.30, 0.03, 0.08),
        "tropical_urban": (32.0, "street", 0.15, 0.25, 0.06),
        "wide_intersection": (42.0, "intersection", 0.18, 0.10, 0.12),
        "rugged_offroad": (36.0, "radial", 0.08, 0.28, 0.08),
        "aerosol_exhaust": (30.0, "street", 0.14, 0.06, 0.08),
        "rain_spray": (38.0, "corridor", 0.10, 0.06, 0.05),
        "snow_clutter": (44.0, "corridor", 0.08, 0.04, 0.04),
        "historic_cobble": (24.0, "canyon", 0.26, 0.06, 0.05),
        "autobahn_ramp": (46.0, "corridor", 0.12, 0.03, 0.07),
        "roundabout_stress": (34.0, "intersection", 0.16, 0.08, 0.22),
        "dust_stress": (40.0, "radial", 0.08, 0.03, 0.06),
        "mountain_foothill": (52.0, "mountain", 0.06, 0.30, 0.05),
        "campus_lightweight": (18.0, "street", 0.08, 0.20, 0.03),
    }
    range_max, layout, structure_ratio, vegetation_ratio, dynamic_ratio = profile.get(
        scene, (40.0, "radial", 0.15, 0.10, 0.08)
    )

    # 1. Ground plane generation (rings/grid)
    n_ground = int(num_pts * (1.0 - structure_ratio - vegetation_ratio - dynamic_ratio))
    r = np.random.uniform(1.0, range_max, n_ground)
    if layout in {"corridor", "canyon"}:
        theta = np.random.normal(0.0, 0.18, n_ground)
    elif layout == "street":
        theta = np.random.normal(0.0, 0.35, n_ground)
    elif layout == "intersection":
        branch = np.random.choice([0.0, np.pi / 2], n_ground)
        theta = branch + np.random.normal(0.0, 0.12, n_ground)
    elif layout == "mountain":
        theta = np.random.uniform(-np.pi * 0.7, np.pi * 0.7, n_ground)
    else:
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

    # 2-4. Scene-specific landmarks. Each archetype intentionally uses a
    # different spatial arrangement so the comparison view is not just a
    # recolored copy of the same road, blocks, and cars.
    n_struct = max(8, int(num_pts * structure_ratio))
    n_veg = max(4, int(num_pts * vegetation_ratio))
    n_dyn = max(3, int(num_pts * dynamic_ratio))

    def append_points(xyz, semantic, is_dynamic=False, signal=(0.5, 0.8)):
        points.append(np.asarray(xyz, dtype=np.float32))
        labels.append(np.full(len(xyz), semantic, dtype=np.int32))
        dynamic.append(np.full(len(xyz), int(is_dynamic), dtype=np.int32))
        intensity.append(np.random.uniform(signal[0], signal[1], len(xyz)))

    def add_box(count, x_range, y_range, z_range, semantic):
        xyz = np.column_stack([
            np.random.uniform(*x_range, count),
            np.random.uniform(*y_range, count),
            np.random.uniform(*z_range, count),
        ])
        append_points(xyz, semantic)

    if scene in {"urban_dense", "urban_canyon"}:
        # Continuous facade walls, with the canyon using much taller towers.
        height = (0.0, 16.0) if scene == "urban_canyon" else (-1.4, 7.0)
        for side in (-1.0, 1.0):
            add_box(n_struct // 2, (2.0, range_max), (side * 14.0, side * 7.0), height, SemanticClass.BUILDING)
    elif scene == "residential":
        # Separated low houses with front yards rather than a solid wall.
        for x in np.linspace(4.0, min(range_max - 2.0, 24.0), 5):
            for side in (-1.0, 1.0):
                add_box(max(4, n_struct // 10), (x - 1.2, x + 1.2), (side * 10.0, side * 6.5), (-1.4, 2.5), SemanticClass.BUILDING)
    elif scene in {"highway", "autobahn_ramp", "rain_spray", "snow_clutter"}:
        # Long parallel barriers; weather scenes add a different raised edge.
        for side in (-1.0, 1.0):
            add_box(n_struct // 2, (1.0, range_max), (side * 5.6, side * 5.1), (-1.3, 0.0), SemanticClass.WALL)
        if scene == "snow_clutter":
            add_box(n_struct // 3, (4.0, range_max * 0.9), (-9.0, -6.5), (-1.4, 1.2), SemanticClass.OBSTACLE)
            add_box(n_struct // 3, (4.0, range_max * 0.9), (6.5, 9.0), (-1.4, 1.2), SemanticClass.OBSTACLE)
    elif scene in {"tropical_urban", "campus_lightweight"}:
        # Discrete canopy clusters and slim trunks, not buildings on both sides.
        tree_x = np.random.uniform(3.0, range_max * 0.9, n_veg)
        tree_y = np.random.choice([-1.0, 1.0], n_veg) * np.random.uniform(5.0, 12.0, n_veg)
        tree_z = np.random.uniform(1.0, 8.0, n_veg)
        append_points(np.column_stack([tree_x, tree_y, tree_z]), SemanticClass.VEGETATION, signal=(0.15, 0.45))
        add_box(n_struct, (3.0, range_max * 0.8), (-4.0, 4.0), (-1.2, 0.8), SemanticClass.WALL)
    elif scene == "wide_intersection":
        # Four approach arms plus signal poles around the junction.
        for x0, y0 in ((range_max * 0.55, 0.0), (0.0, range_max * 0.55), (range_max * 0.55, 0.0), (0.0, -range_max * 0.55)):
            add_box(n_struct // 8, (x0 - 1.0, x0 + 1.0), (y0 - 8.0, y0 + 8.0), (-1.4, 4.5), SemanticClass.OBSTACLE)
    elif scene in {"rugged_offroad", "dust_stress", "mountain_foothill"}:
        # Scattered boulders and rock outcrops define an off-road scene.
        bx = np.random.uniform(3.0, range_max, n_struct)
        by = np.random.uniform(-11.0, 11.0, n_struct)
        bz = np.random.uniform(-1.2, 2.5 if scene != "mountain_foothill" else 7.0, n_struct)
        append_points(np.column_stack([bx, by, bz]), SemanticClass.OBSTACLE)
    elif scene == "historic_cobble":
        # Low irregular stone walls with an open street center.
        add_box(n_struct // 2, (2.0, range_max), (-9.0, -6.5), (-1.4, 3.0), SemanticClass.WALL)
        add_box(n_struct // 2, (2.0, range_max), (6.5, 9.0), (-1.4, 3.0), SemanticClass.WALL)
    elif scene == "roundabout_stress":
        # Circular central island and radial approaches.
        angles = np.random.uniform(0.0, 2.0 * np.pi, n_struct)
        radius = np.random.uniform(4.0, 6.0, n_struct)
        append_points(np.column_stack([12.0 + radius * np.cos(angles), radius * np.sin(angles), np.random.uniform(-1.3, 0.6, n_struct)]), SemanticClass.WALL)
    else:
        add_box(n_struct, (2.0, range_max), (-10.0, 10.0), (-1.4, 4.0), SemanticClass.WALL)

    if scene not in {"tropical_urban", "campus_lightweight"}:
        vx = np.random.uniform(3.0, range_max * 0.9, n_veg)
        vy = np.random.uniform(-10.0, 10.0, n_veg)
        vz = np.random.uniform(0.0, 7.0, n_veg)
        append_points(np.column_stack([vx, vy, vz]), SemanticClass.VEGETATION, signal=(0.15, 0.45))
    elif scene == "campus_lightweight":
        add_box(n_veg, (3.0, range_max * 0.9), (-8.0, 8.0), (-1.2, 1.0), SemanticClass.OBSTACLE)

    if scene == "roundabout_stress":
        angles = np.random.uniform(0.0, 2.0 * np.pi, n_dyn)
        radius = np.random.uniform(7.0, 11.0, n_dyn)
        dyn_pts = np.column_stack([12.0 + radius * np.cos(angles), radius * np.sin(angles), np.random.uniform(-1.4, 0.3, n_dyn)])
    elif scene == "wide_intersection":
        dyn_pts = np.column_stack([
            np.random.uniform(5.0, 24.0, n_dyn),
            np.random.choice([-1.0, 1.0], n_dyn) * np.random.uniform(0.5, 4.0, n_dyn),
            np.random.uniform(-1.4, 0.4, n_dyn),
        ])
    elif scene in {"highway", "autobahn_ramp", "rain_spray", "snow_clutter"}:
        dyn_pts = np.column_stack([
            np.random.uniform(6.0, range_max, n_dyn),
            np.random.uniform(-2.8, 2.8, n_dyn),
            np.random.uniform(-1.4, 0.4, n_dyn),
        ])
    elif scene == "campus_lightweight":
        dyn_pts = np.column_stack([
            np.random.uniform(5.0, range_max, n_dyn),
            np.random.uniform(-5.0, 5.0, n_dyn),
            np.random.uniform(-1.4, 0.4, n_dyn),
        ])
    else:
        dyn_pts = np.column_stack([
            np.random.uniform(5.0, min(range_max, 26.0), n_dyn),
            np.random.uniform(-4.0, 4.0, n_dyn),
            np.random.uniform(-1.4, 0.4, n_dyn),
        ])
    append_points(dyn_pts, SemanticClass.VEHICLE, is_dynamic=True, signal=(0.6, 0.95))

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
        points, labels, dyn = generate_point_cloud_for_scenario(sc)

        # Save frame 000000.bin / npz
        np.savez_compressed(
            frames_dir / "frame_000.npz",
            points=points.astype(np.float32),
            labels=labels.astype(np.int32),
            dynamic=dyn.astype(np.int32)
        )

        metadata = {
            **sc,
            "scene_signature": SCENE_SIGNATURES.get(sc["scene_type"], sc["scene_type"]),
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
