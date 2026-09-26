"""Dataset-specific adapters mapping raw formats to standardized ScenarioFrame.
Provides exact provenance, license tracking, and ontology translation.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from .base_adapter import BaseDatasetAdapter, ScenarioFrame
from ..processing.semantics.ontology import SemanticClass

class SemanticKITTIAdapter(BaseDatasetAdapter):
    """Adapter for SemanticKITTI 360-degree LiDAR dataset."""
    def __init__(self):
        super().__init__(
            dataset_name="SemanticKITTI",
            source_url="http://www.semantic-kitti.org/",
            license_name="Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)"
        )
        # Mapping from KITTI learning IDs to VISTAR SemanticClass
        self.label_map = {
            0: SemanticClass.UNKNOWN,       # unlabeled / outlier
            1: SemanticClass.VEHICLE,       # car
            2: SemanticClass.CYCLIST,       # bicycle
            3: SemanticClass.CYCLIST,       # motorcycle
            4: SemanticClass.VEHICLE,       # truck
            5: SemanticClass.VEHICLE,       # other-vehicle
            6: SemanticClass.PEDESTRIAN,    # person
            7: SemanticClass.PEDESTRIAN,    # bicyclist
            8: SemanticClass.CYCLIST,       # motorcyclist
            9: SemanticClass.ROAD,          # road
            10: SemanticClass.ROAD,         # parking
            11: SemanticClass.ROAD,         # sidewalk
            12: SemanticClass.GROUND,       # other-ground
            13: SemanticClass.BUILDING,     # building
            14: SemanticClass.WALL,         # fence
            15: SemanticClass.VEGETATION,   # vegetation
            16: SemanticClass.VEGETATION,   # trunk
            17: SemanticClass.GRASS,        # terrain
            18: SemanticClass.OBSTACLE,     # pole
            19: SemanticClass.OBSTACLE,     # traffic-sign
        }

    def map_labels(self, raw_labels: np.ndarray) -> np.ndarray:
        return np.vectorize(lambda x: self.label_map.get(int(x) & 0xFFFF, SemanticClass.UNKNOWN))(raw_labels)

class NuScenesAdapter(BaseDatasetAdapter):
    """Adapter for Motional nuScenes LiDAR dataset (Boston & Singapore)."""
    def __init__(self):
        super().__init__(
            dataset_name="nuScenes",
            source_url="https://www.nuscenes.org/",
            license_name="CC BY-NC-SA 4.0"
        )
        self.label_map = {
            0: SemanticClass.UNKNOWN,
            1: SemanticClass.OBSTACLE,     # barrier
            2: SemanticClass.CYCLIST,      # bicycle
            3: SemanticClass.VEHICLE,      # bus
            4: SemanticClass.VEHICLE,      # car
            5: SemanticClass.VEHICLE,      # construction vehicle
            6: SemanticClass.CYCLIST,      # motorcycle
            7: SemanticClass.PEDESTRIAN,   # pedestrian
            8: SemanticClass.OBSTACLE,     # traffic cone
            9: SemanticClass.VEHICLE,      # trailer
            10: SemanticClass.VEHICLE,     # truck
            11: SemanticClass.ROAD,        # drivable surface
            12: SemanticClass.ROAD,        # sidewalk
            13: SemanticClass.GRASS,       # terrain
            14: SemanticClass.BUILDING,    # manmade
            15: SemanticClass.VEGETATION,  # vegetation
        }

    def map_labels(self, raw_labels: np.ndarray) -> np.ndarray:
        return np.vectorize(lambda x: self.label_map.get(int(x), SemanticClass.UNKNOWN))(raw_labels)

class WaymoAdapter(BaseDatasetAdapter):
    """Adapter for Waymo Open Dataset (Multi-city US)."""
    def __init__(self):
        super().__init__(
            dataset_name="Waymo Open Dataset",
            source_url="https://waymo.com/open/",
            license_name="Waymo Dataset License Agreement for Non-Commercial Use"
        )
        self.label_map = {
            0: SemanticClass.UNKNOWN,
            1: SemanticClass.VEHICLE,      # Car
            2: SemanticClass.PEDESTRIAN,   # Pedestrian
            3: SemanticClass.OBSTACLE,     # Sign
            4: SemanticClass.CYCLIST,      # Cyclist
        }

    def map_labels(self, raw_labels: np.ndarray) -> np.ndarray:
        return np.vectorize(lambda x: self.label_map.get(int(x), SemanticClass.UNKNOWN))(raw_labels)

class PandaSetAdapter(BaseDatasetAdapter):
    """Adapter for Hesai & Scale AI PandaSet with aerosol/smoke/exhaust annotations."""
    def __init__(self):
        super().__init__(
            dataset_name="PandaSet",
            source_url="https://pandaset.org/",
            license_name="CC BY 4.0 (Scale AI & Hesai)"
        )
        self.label_map = {
            0: SemanticClass.UNKNOWN,
            1: SemanticClass.SMOKE,        # Smoke / Exhaust
            2: SemanticClass.VEHICLE,      # Car
            3: SemanticClass.VEHICLE,      # Pickup Truck
            4: SemanticClass.VEHICLE,      # Medium-duty Truck
            5: SemanticClass.PEDESTRIAN,   # Pedestrian
            6: SemanticClass.CYCLIST,      # Motorized Scooter / Bicycle
            7: SemanticClass.ROAD,         # Drivable Ground
            8: SemanticClass.GRASS,        # Soft Ground / Lawn
            9: SemanticClass.BUILDING,     # Buildings
            10: SemanticClass.VEGETATION,  # Vegetation
        }

    def map_labels(self, raw_labels: np.ndarray) -> np.ndarray:
        return np.vectorize(lambda x: self.label_map.get(int(x), SemanticClass.UNKNOWN))(raw_labels)

class RELLISAdapter(BaseDatasetAdapter):
    """Adapter for RELLIS-3D Off-Road Unstructured Terrain Dataset."""
    def __init__(self):
        super().__init__(
            dataset_name="RELLIS-3D",
            source_url="https://github.com/unmannedlab/RELLIS-3D",
            license_name="BSD 3-Clause License"
        )
        self.label_map = {
            0: SemanticClass.UNKNOWN,
            1: SemanticClass.GRASS,        # grass
            2: SemanticClass.VEGETATION,   # tree
            3: SemanticClass.VEGETATION,   # bush
            4: SemanticClass.GROUND,       # dirt
            5: SemanticClass.MUD,          # mud
            6: SemanticClass.WATER,        # puddle
            7: SemanticClass.OBSTACLE,     # rubble
            8: SemanticClass.OBSTACLE,     # barrier
            9: SemanticClass.GROUND,       # log
            10: SemanticClass.OBSTACLE,    # object
            11: SemanticClass.ROAD,        # concrete
        }

    def map_labels(self, raw_labels: np.ndarray) -> np.ndarray:
        return np.vectorize(lambda x: self.label_map.get(int(x), SemanticClass.UNKNOWN))(raw_labels)

class BoreasAdapter(BaseDatasetAdapter):
    """Adapter for Boreas (Rain / Snow / Adverse Weather) Dataset."""
    def __init__(self):
        super().__init__(
            dataset_name="Boreas",
            source_url="https://www.boreas.utias.utoronto.ca/",
            license_name="CC BY-NC-SA 4.0"
        )
        self.label_map = {
            0: SemanticClass.UNKNOWN,
            1: SemanticClass.ROAD,
            2: SemanticClass.GROUND,
            3: SemanticClass.VEHICLE,
            4: SemanticClass.PEDESTRIAN,
            5: SemanticClass.BUILDING,
            6: SemanticClass.VEGETATION,
            7: SemanticClass.SMOKE,        # Atmospheric precipitation/snow spray
        }

    def map_labels(self, raw_labels: np.ndarray) -> np.ndarray:
        return np.vectorize(lambda x: self.label_map.get(int(x), SemanticClass.UNKNOWN))(raw_labels)

class OxfordRobotCarAdapter(BaseDatasetAdapter):
    """Adapter for Oxford RobotCar Long-Term Traversal Dataset."""
    def __init__(self):
        super().__init__(
            dataset_name="Oxford RobotCar",
            source_url="https://robotcar-dataset.robots.ox.ac.uk/",
            license_name="CC BY-NC-SA 4.0"
        )
        self.label_map = {
            0: SemanticClass.UNKNOWN,
            1: SemanticClass.ROAD,
            2: SemanticClass.BUILDING,
            3: SemanticClass.VEGETATION,
            4: SemanticClass.VEHICLE,
            5: SemanticClass.PEDESTRIAN,
        }

    def map_labels(self, raw_labels: np.ndarray) -> np.ndarray:
        return np.vectorize(lambda x: self.label_map.get(int(x), SemanticClass.UNKNOWN))(raw_labels)

class A2D2Adapter(BaseDatasetAdapter):
    """Adapter for Audi Autonomous Driving Dataset (A2D2) Multi-LiDAR."""
    def __init__(self):
        super().__init__(
            dataset_name="Audi Autonomous Driving Dataset (A2D2)",
            source_url="https://www.a2d2.audi/",
            license_name="CC BY-ND 4.0"
        )
        self.label_map = {
            0: SemanticClass.UNKNOWN,
            1: SemanticClass.ROAD,
            2: SemanticClass.BUILDING,
            3: SemanticClass.VEHICLE,
            4: SemanticClass.PEDESTRIAN,
            5: SemanticClass.CYCLIST,
            6: SemanticClass.VEGETATION,
            7: SemanticClass.OBSTACLE,
        }

    def map_labels(self, raw_labels: np.ndarray) -> np.ndarray:
        return np.vectorize(lambda x: self.label_map.get(int(x), SemanticClass.UNKNOWN))(raw_labels)

class DEMAdapter(BaseDatasetAdapter):
    """Adapter for Digital Elevation Models (Copernicus GLO-90, USGS 3DEP, CartoDEM)."""
    def __init__(self, dem_type: str = "Copernicus GLO-90"):
        super().__init__(
            dataset_name=dem_type,
            source_url="https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model",
            license_name="Copernicus Open Access / Public Domain / ISRO Open Data"
        )
