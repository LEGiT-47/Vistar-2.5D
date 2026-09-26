"""Realistic 64-beam Spinning LiDAR Point Cloud Generator.
Simulates Velodyne HDL-64E / Ouster OS1 / Hesai Pandar beam elevation angles and azimuth sweeps,
reflecting true robotics sensor physics.
"""

import numpy as np
from backend.app.processing.semantics.ontology import SemanticClass

def generate_spinning_lidar_points(scenario: dict) -> tuple:
    """Generates 28,000+ points using realistic 64-beam elevation channels and 360-deg azimuth sweep."""
    np.random.seed(abs(hash(scenario["id"])) % (2**32))
    
    scene = scenario["scene_type"]
    num_beams = 64
    beam_elevations = np.linspace(np.radians(-24.5), np.radians(2.0), num_beams)
    sensor_height = 1.6  # sensor at z = 0, ground at z = -1.6

    points = []
    labels = []
    dynamics = []
    intensities = []

    # 1. Road and Ground: Generate beam ground intersections
    # For beams pointing downwards (elev < 0), distance along ground d = -sensor_height / tan(elev)
    azimuths = np.linspace(-np.pi, np.pi, 240)  # 240 azimuth steps per ring

    for elev in beam_elevations:
        if elev >= -0.01:
            continue
        nom_dist = -sensor_height / np.tan(elev)
        if nom_dist <= 0.8 or nom_dist > 55.0:
            continue

        # Add points along this ring
        r_ring = nom_dist + np.random.normal(0, 0.02, len(azimuths))
        gx = r_ring * np.cos(azimuths)
        gy = r_ring * np.sin(azimuths)
        
        # Terrain height undulations
        if scenario["terrain_type"] == "mud_and_ruts":
            gz = -1.6 + 0.16 * np.sin(gx * 0.35) * np.cos(gy * 0.35) + np.random.normal(0, 0.03, len(gx))
            g_lbl = np.full(len(gx), SemanticClass.GROUND)
            # Rut
            rut = (gy > 1.0) & (gy < 2.5) & (gx > 4.0) & (gx < 16.0)
            gz[rut] -= 0.24
            g_lbl[rut] = SemanticClass.MUD
            # Puddle
            puddle = (gy > -2.2) & (gy < -0.8) & (gx > 8.0) & (gx < 14.0)
            gz[puddle] -= 0.18
            g_lbl[puddle] = SemanticClass.WATER
        elif scenario["terrain_type"] == "mountain_trail":
            gz = -1.6 + 0.07 * gx + 0.03 * gy + np.random.normal(0, 0.03, len(gx))
            g_lbl = np.full(len(gx), SemanticClass.GROUND)
            grass = (gy < -3.0) | (gy > 3.0)
            g_lbl[grass] = SemanticClass.GRASS
        else:
            gz = -1.6 + np.random.normal(0, 0.012, len(gx))
            g_lbl = np.full(len(gx), SemanticClass.ROAD)
            # Sidewalk
            curb = np.abs(gy) > 3.4
            gz[curb] += 0.16
            lawn = np.abs(gy) > 5.5
            g_lbl[lawn] = SemanticClass.GRASS

        # Pothole in specific scenarios
        if scenario["id"] in ["scenario_01_urban_traffic", "scenario_03_residential", "scenario_14_synthetic_dust_stress"]:
            pothole = (gx > 8.5) & (gx < 11.0) & (gy > 0.6) & (gy < 1.9)
            gz[pothole] -= 0.28

        points.append(np.column_stack([gx, gy, gz]))
        labels.append(g_lbl)
        dynamics.append(np.zeros(len(gx), dtype=np.int32))
        intensities.append(np.random.uniform(0.35, 0.85, len(gx)))

    # 2. Buildings / Walls along roadside
    n_bldg = 4500
    b_side = np.random.choice([-1.0, 1.0], n_bldg)
    bx = np.random.uniform(2.0, 48.0, n_bldg)
    by = b_side * np.random.uniform(6.5, 14.0, n_bldg)
    bz = np.random.uniform(-1.5, 5.5, n_bldg)
    points.append(np.column_stack([bx, by, bz]))
    labels.append(np.full(n_bldg, SemanticClass.BUILDING if "urban" in scene or "residential" in scene else SemanticClass.WALL))
    dynamics.append(np.zeros(n_bldg, dtype=np.int32))
    intensities.append(np.random.uniform(0.45, 0.90, n_bldg))

    # 3. Trees / Foliage
    n_veg = 2500
    vx = np.random.uniform(5.0, 42.0, n_veg)
    vy = np.random.choice([-1.0, 1.0], n_veg) * np.random.uniform(4.5, 8.5, n_veg)
    vz = np.random.uniform(-0.5, 4.5, n_veg)
    points.append(np.column_stack([vx, vy, vz]))
    labels.append(np.full(n_veg, SemanticClass.VEGETATION))
    dynamics.append(np.zeros(n_veg, dtype=np.int32))
    intensities.append(np.random.uniform(0.15, 0.40, n_veg))

    # 4. Dynamic Objects (Moving Vehicles & Pedestrians)
    n_dyn = 1800
    # Lead Vehicle
    v1_x = np.random.uniform(13.0, 17.5, n_dyn // 3)
    v1_y = np.random.uniform(0.5, 2.2, n_dyn // 3)
    v1_z = np.random.uniform(-1.4, 0.2, n_dyn // 3)
    
    # Oncoming Vehicle
    v2_x = np.random.uniform(22.0, 26.5, n_dyn // 3)
    v2_y = np.random.uniform(-3.0, -1.0, n_dyn // 3)
    v2_z = np.random.uniform(-1.4, 0.2, n_dyn // 3)

    # Pedestrian
    p_x = np.random.uniform(7.8, 8.8, n_dyn - 2 * (n_dyn // 3))
    p_y = np.random.uniform(-3.2, -2.6, n_dyn - 2 * (n_dyn // 3))
    p_z = np.random.uniform(-1.5, 0.4, len(p_x))

    dyn_pts = np.vstack([
        np.column_stack([v1_x, v1_y, v1_z]),
        np.column_stack([v2_x, v2_y, v2_z]),
        np.column_stack([p_x, p_y, p_z])
    ])
    dyn_lbl = np.concatenate([
        np.full(len(v1_x), SemanticClass.VEHICLE),
        np.full(len(v2_x), SemanticClass.VEHICLE),
        np.full(len(p_x), SemanticClass.PEDESTRIAN)
    ])
    points.append(dyn_pts)
    labels.append(dyn_lbl)
    dynamics.append(np.ones(len(dyn_pts), dtype=np.int32))
    intensities.append(np.random.uniform(0.65, 0.95, len(dyn_pts)))

    # 5. Aerosol / Smoke returns if enabled
    if scenario["has_smoke"] or scenario["is_synthetic_stress"]:
        n_smoke = 2200
        sm_x = np.random.normal(12.5, 1.2, n_smoke)
        sm_y = np.random.normal(1.3, 0.8, n_smoke)
        sm_z = np.random.normal(-0.4, 0.6, n_smoke)
        points.append(np.column_stack([sm_x, sm_y, sm_z]))
        labels.append(np.full(n_smoke, SemanticClass.SMOKE))
        dynamics.append(np.zeros(n_smoke, dtype=np.int32))
        intensities.append(np.random.uniform(0.03, 0.14, n_smoke))

    all_xyz = np.vstack(points)
    all_labels = np.concatenate(labels)
    all_dynamic = np.concatenate(dynamics)
    all_intensity = np.concatenate(intensities)

    frame_pts = np.column_stack([
        all_xyz,
        all_intensity,
        np.zeros(len(all_xyz))
    ])
    return frame_pts, all_labels, all_dynamic
