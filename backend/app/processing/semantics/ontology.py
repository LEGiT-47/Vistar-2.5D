"""Standardized semantic ontology for VISTAR-2.5D.
Harmonizes diverse datasets (SemanticKITTI, nuScenes, Waymo, PandaSet, RELLIS-3D, etc.)
into a unified robotics perception legend.
"""

from enum import IntEnum
from typing import Dict, Any, Tuple

class SemanticClass(IntEnum):
    UNKNOWN = 0
    GROUND = 1
    ROAD = 2
    GRASS = 3
    VEGETATION = 4
    MUD = 5
    WATER = 6
    BUILDING = 7
    WALL = 8
    VEHICLE = 9
    PEDESTRIAN = 10
    CYCLIST = 11
    OBSTACLE = 12
    SMOKE = 13

ONTOLOGY_METADATA: Dict[int, Dict[str, Any]] = {
    SemanticClass.UNKNOWN: {
        "name": "UNKNOWN",
        "color": [128, 128, 128],       # Gray #808080
        "hex": "#808080",
        "traversability_base": 0.5,
        "is_static": True,
        "description": "Unclassified or low-confidence return"
    },
    SemanticClass.GROUND: {
        "name": "GROUND",
        "color": [150, 110, 80],        # Earth Brown #966e50
        "hex": "#966e50",
        "traversability_base": 0.85,
        "is_static": True,
        "description": "Firm ground, gravel, or compact soil"
    },
    SemanticClass.ROAD: {
        "name": "ROAD",
        "color": [60, 180, 240],        # Cyan/Blue #3cb4f0
        "hex": "#3cb4f0",
        "traversability_base": 1.0,
        "is_static": True,
        "description": "Asphalt, paved surfaces, lane corridor"
    },
    SemanticClass.GRASS: {
        "name": "GRASS",
        "color": [80, 200, 120],        # Emerald #50c878
        "hex": "#50c878",
        "traversability_base": 0.75,
        "is_static": True,
        "description": "Low lawn, roadside grass, negotiable"
    },
    SemanticClass.VEGETATION: {
        "name": "VEGETATION",
        "color": [34, 139, 34],         # Forest Green #228b22
        "hex": "#228b22",
        "traversability_base": 0.2,
        "is_static": True,
        "description": "Dense shrubs, trees, canopy returns"
    },
    SemanticClass.MUD: {
        "name": "MUD",
        "color": [139, 69, 19],         # Saddle Brown #8b4513
        "hex": "#8b4513",
        "traversability_base": 0.35,
        "is_static": True,
        "description": "Saturated soil, rutted terrain, slip risk"
    },
    SemanticClass.WATER: {
        "name": "WATER",
        "color": [30, 144, 255],        # Deep Sky Blue #1e90ff
        "hex": "#1e90ff",
        "traversability_base": 0.05,
        "is_static": True,
        "description": "Puddle, canal, water hazard"
    },
    SemanticClass.BUILDING: {
        "name": "BUILDING",
        "color": [178, 34, 34],         # Firebrick #b22222
        "hex": "#b22222",
        "traversability_base": 0.0,
        "is_static": True,
        "description": "Permanent architectural structure"
    },
    SemanticClass.WALL: {
        "name": "WALL",
        "color": [210, 105, 30],        # Chocolate #d2691e
        "hex": "#d2691e",
        "traversability_base": 0.0,
        "is_static": True,
        "description": "Barrier, fence, retention wall"
    },
    SemanticClass.VEHICLE: {
        "name": "VEHICLE",
        "color": [255, 165, 0],         # Amber #ffa500
        "hex": "#ffa500",
        "traversability_base": 0.0,
        "is_static": False,
        "description": "Cars, trucks, buses, heavy equipment"
    },
    SemanticClass.PEDESTRIAN: {
        "name": "PEDESTRIAN",
        "color": [255, 69, 0],          # Red-Orange #ff4500
        "hex": "#ff4500",
        "traversability_base": 0.0,
        "is_static": False,
        "description": "Pedestrians, standing or walking persons"
    },
    SemanticClass.CYCLIST: {
        "name": "CYCLIST",
        "color": [255, 215, 0],         # Gold #ffd700
        "hex": "#ffd700",
        "traversability_base": 0.0,
        "is_static": False,
        "description": "Bicyclists, motorcyclists"
    },
    SemanticClass.OBSTACLE: {
        "name": "OBSTACLE",
        "color": [220, 20, 60],         # Crimson #dc143c
        "hex": "#dc143c",
        "traversability_base": 0.0,
        "is_static": True,
        "description": "Poles, debris, bollards, boulders"
    },
    SemanticClass.SMOKE: {
        "name": "SMOKE",
        "color": [176, 196, 222],       # Light Steel Blue (Aerosol) #b0c4de
        "hex": "#b0c4de",
        "traversability_base": 0.9,     # Aerosol is mechanically traversable if ground is clear
        "is_static": False,
        "description": "Exhaust, smoke, aerosol returns (low-confidence)"
    },
}

def get_class_name(class_id: int) -> str:
    return ONTOLOGY_METADATA.get(class_id, ONTOLOGY_METADATA[SemanticClass.UNKNOWN])["name"]

def get_class_color_rgb(class_id: int) -> Tuple[int, int, int]:
    col = ONTOLOGY_METADATA.get(class_id, ONTOLOGY_METADATA[SemanticClass.UNKNOWN])["color"]
    return (col[0], col[1], col[2])

def get_class_hex(class_id: int) -> str:
    return ONTOLOGY_METADATA.get(class_id, ONTOLOGY_METADATA[SemanticClass.UNKNOWN])["hex"]

def get_traversability_base(class_id: int) -> float:
    return ONTOLOGY_METADATA.get(class_id, ONTOLOGY_METADATA[SemanticClass.UNKNOWN])["traversability_base"]
