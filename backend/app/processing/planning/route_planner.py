"""A* Traversability-Aware Route Planner.
Finds optimal navigation corridor over VISTAR 2.5D grid, penalizing risk, steep slope, roughness,
uncertainty, and dynamic obstacles.
"""

import heapq
from typing import Dict, Any, List, Tuple, Optional
import numpy as np

class RoutePlanner:
    def __init__(self, blocked_traversability_threshold: float = 0.25):
        self.blocked_thresh = blocked_traversability_threshold

    def plan_path(
        self,
        cells: Dict[str, Any],
        start_xy: Tuple[float, float],
        goal_xy: Tuple[float, float],
        grid_step: float = 0.40
    ) -> Dict[str, Any]:
        """Runs A* path search over the traversability landscape.
        
        Returns:
            path: List of [x, y, z] waypoints
            path_length_m: total distance
            status: "SUCCESS" | "BLOCKED" | "PARTIAL"
        """
        # Quantize start and goal to grid coordinates
        start_node = (round(start_xy[0] / grid_step) * grid_step, round(start_xy[1] / grid_step) * grid_step)
        goal_node = (round(goal_xy[0] / grid_step) * grid_step, round(goal_xy[1] / grid_step) * grid_step)

        # Build fast spatial lookup for cell traversability
        # Use KDTree or nearest cell matching
        cell_coords = []
        cell_costs = []
        cell_z = []

        for cell in (cells.values() if isinstance(cells, dict) else cells):
            cx = cell.x if hasattr(cell, 'x') else cell['x']
            cy = cell.y if hasattr(cell, 'y') else cell['y']
            cz = cell.elevation_mean if hasattr(cell, 'elevation_mean') else cell['elevation_mean']
            trav = cell.traversability if hasattr(cell, 'traversability') else cell['traversability']
            dyn = cell.dynamic_probability if hasattr(cell, 'dynamic_probability') else cell.get('dynamic_probability', 0.0)
            uncert = cell.uncertainty if hasattr(cell, 'uncertainty') else cell.get('uncertainty', 0.0)

            # Cost calculation: 1.0 (free) to infinity (blocked)
            effective_trav = trav * (1.0 - dyn * 0.9) * (1.0 - uncert * 0.4)
            if effective_trav < self.blocked_thresh:
                cost = 999.0  # Blocked
            else:
                cost = 1.0 + (1.0 - effective_trav) * 8.0

            cell_coords.append((cx, cy))
            cell_costs.append(cost)
            cell_z.append(cz)

        cell_coords_np = np.array(cell_coords)
        if len(cell_coords_np) == 0:
            # Direct straight line fallback if no cells
            return {
                "status": "FALLBACK_DIRECT",
                "waypoints": [[start_xy[0], start_xy[1], -1.6], [goal_xy[0], goal_xy[1], -1.6]],
                "path_length_m": float(np.linalg.norm(np.array(goal_xy) - np.array(start_xy))),
                "traversable": True
            }

        # Priority queue for A*: (f_score, current_node)
        open_set = []
        heapq.heappush(open_set, (0.0, start_node))
        came_from: Dict[Tuple[float, float], Tuple[float, float]] = {}
        g_score: Dict[Tuple[float, float], float] = {start_node: 0.0}

        def heuristic(a: Tuple[float, float], b: Tuple[float, float]) -> float:
            return float(np.hypot(b[0] - a[0], b[1] - a[1]))

        def get_cost_at(pt: Tuple[float, float]) -> Tuple[float, float]:
            dists = np.linalg.norm(cell_coords_np - np.array(pt), axis=1)
            min_idx = int(np.argmin(dists))
            if dists[min_idx] > 2.5:
                return 1.5, -1.6  # Default open terrain outside tight sensor bounds
            return cell_costs[min_idx], cell_z[min_idx]

        found_goal = False
        best_node = start_node
        best_dist_to_goal = heuristic(start_node, goal_node)
        iterations = 0

        # 8-connectivity motion offsets
        moves = [
            (grid_step, 0.0), (-grid_step, 0.0),
            (0.0, grid_step), (0.0, -grid_step),
            (grid_step, grid_step), (-grid_step, -grid_step),
            (grid_step, -grid_step), (-grid_step, grid_step)
        ]

        while open_set and iterations < 1200:
            iterations += 1
            _, current = heapq.heappop(open_set)

            if heuristic(current, goal_node) <= grid_step * 1.5:
                found_goal = True
                best_node = current
                break

            current_dist = heuristic(current, goal_node)
            if current_dist < best_dist_to_goal:
                best_dist_to_goal = current_dist
                best_node = current

            for dx, dy in moves:
                neighbor = (round(current[0] + dx, 2), round(current[1] + dy, 2))
                step_dist = np.hypot(dx, dy)
                cell_cost, _ = get_cost_at(neighbor)
                
                if cell_cost >= 900.0:  # impassable
                    continue

                tentative_g = g_score[current] + step_dist * cell_cost
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + heuristic(neighbor, goal_node) * 1.1
                    heapq.heappush(open_set, (f, neighbor))

        # Reconstruct path
        path_nodes = [best_node]
        curr = best_node
        while curr in came_from:
            curr = came_from[curr]
            path_nodes.append(curr)
        path_nodes.reverse()

        # Build 3D waypoints with elevation
        waypoints = []
        for nx, ny in path_nodes:
            _, z_val = get_cost_at((nx, ny))
            waypoints.append([round(nx, 2), round(ny, 2), round(z_val + 0.15, 2)])

        # Calculate path length
        path_len = 0.0
        for i in range(len(waypoints) - 1):
            p1 = np.array(waypoints[i][:2])
            p2 = np.array(waypoints[i+1][:2])
            path_len += float(np.linalg.norm(p2 - p1))

        return {
            "status": "SUCCESS" if found_goal else "PARTIAL",
            "waypoints": waypoints,
            "path_length_m": round(path_len, 2),
            "start": list(start_xy),
            "goal": list(goal_xy),
            "reached_goal": found_goal,
            "waypoint_count": len(waypoints)
        }
