"""ROS 2 Architecture Abstraction and Topic Serialization.
Implements ROS 2 DDS-compatible topic abstractions for seamless robotics integration:
- /vistar/raw_points (sensor_msgs/msg/PointCloud2)
- /vistar/adaptive_grid (vistar_msgs/msg/AdaptiveGrid25D)
- /vistar/traversability_map (nav_msgs/msg/OccupancyGrid)
- /vistar/planned_path (nav_msgs/msg/Path)
- /vistar/dynamic_obstacles (visualization_msgs/msg/MarkerArray)
"""

from typing import Dict, Any, List
import json

class ROS2BridgeAbstraction:
    def __init__(self, node_name: str = "vistar_adaptive_mapper_node"):
        self.node_name = node_name
        self.published_topics = {
            "/vistar/raw_points": {
                "type": "sensor_msgs/msg/PointCloud2",
                "rate_hz": 10,
                "qos": "BEST_EFFORT",
                "description": "Raw or filtered LiDAR point stream in base_link or map frame"
            },
            "/vistar/adaptive_grid": {
                "type": "vistar_msgs/msg/AdaptiveGrid25D",
                "rate_hz": 10,
                "qos": "RELIABLE",
                "description": "Multi-scale variable resolution 2.5D cells with uncertainty and elevation"
            },
            "/vistar/traversability_map": {
                "type": "nav_msgs/msg/OccupancyGrid",
                "rate_hz": 10,
                "qos": "RELIABLE",
                "description": "Nav2-compatible costmap representation for global/local path planners"
            },
            "/vistar/planned_path": {
                "type": "nav_msgs/msg/Path",
                "rate_hz": 5,
                "qos": "RELIABLE",
                "description": "A* optimal hazard-avoiding collision-free corridor"
            },
            "/vistar/dynamic_obstacles": {
                "type": "visualization_msgs/msg/MarkerArray",
                "rate_hz": 15,
                "qos": "BEST_EFFORT",
                "description": "Live transient dynamic actors segregated from persistent terrain"
            },
            "/vistar/dem_context": {
                "type": "nav_msgs/msg/OccupancyGrid",
                "rate_hz": 1,
                "qos": "TRANSIENT_LOCAL",
                "description": "Extended macroscopic terrain context beyond active LiDAR horizon"
            }
        }

    def get_node_graph(self) -> Dict[str, Any]:
        return {
            "node_name": self.node_name,
            "ros_distro": "Humble Hawksbill / Iron Irwini / Rolling",
            "topics": self.published_topics,
            "lifecycle_state": "ACTIVE"
        }
