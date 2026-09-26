"""Base dataset adapter and ScenarioFrame definition.
VISTAR-2.5D Adaptive Variable Resolution Perception.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import numpy as np

@dataclass
class ScenarioFrame:
    """Standardized internal representation of a LiDAR frame across all datasets."""
    # points: Nx5 array [x, y, z, intensity, timestamp_rel]
    points: np.ndarray
    # semantic_labels: N array of integer ontology IDs
    semantic_labels: np.ndarray
    # instance_ids: Optional N array
    instance_ids: Optional[np.ndarray] = None
    # dynamic_labels: Optional N array (1 for moving, 0 for static)
    dynamic_labels: Optional[np.ndarray] = None
    # confidence: Optional N array in [0, 1]
    confidence: Optional[np.ndarray] = None
    # pose: 4x4 ego vehicle transform or [x, y, z, roll, pitch, yaw]
    pose: Optional[Dict[str, float]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: float = 0.0
    frame_id: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert basic summary to dictionary."""
        return {
            "num_points": int(len(self.points)),
            "frame_id": self.frame_id,
            "timestamp": self.timestamp,
            "pose": self.pose,
            "has_semantics": self.semantic_labels is not None,
            "has_instances": self.instance_ids is not None,
            "has_dynamic_labels": self.dynamic_labels is not None,
            "metadata": self.metadata
        }

class BaseDatasetAdapter:
    """Base class for all dataset ingestion adapters."""
    def __init__(self, dataset_name: str, source_url: str, license_name: str):
        self.dataset_name = dataset_name
        self.source_url = source_url
        self.license_name = license_name

    def load_frame(self, file_path: str, frame_idx: int = 0) -> ScenarioFrame:
        raise NotImplementedError("Subclasses must implement load_frame")

    def get_provenance(self) -> Dict[str, str]:
        return {
            "dataset": self.dataset_name,
            "source": self.source_url,
            "license": self.license_name
        }
