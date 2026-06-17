from typing import Literal, Union
from collections import deque
from .shared import *
import random

class Agent:
    def __init__(
        self, 
        init_row: int, 
        init_cols: int,
        vision_range: int, 
        row_size: int,
        col_size: int,
        color: tuple[int, int, int] = (0, 255, 0),
        max_cell_mem: int = 35
    ):
        self.curr_row = init_row
        self.curr_col = init_cols
        self.color_rgb = color
        self.vision_range = vision_range
        
        self.state_collection = ["chase", "patrol", "suspicious"]
        self.curr_state_id = 1
        
        self.walk_speed_mult = 1
        self.patrol_speed_mult = 0.5
        
        self.direction_collection = ["up", "down", "left", "right"]
        self.curr_view_id = random.randrange(len(self.direction_collection))
        self.curr_view_cell = []
        
        self.prob_map = [[0.25 for _ in range(col_size)] for _ in range(row_size)]
        self.checked_list = [(self.curr_row, self.curr_col)]
        self.max_mem = max_cell_mem
        self.hear_player = False
        self.see_player = False

    def cell_in_view(
        self,
        maze: list[list[dict[str, int]]],
    ) -> None: # Code corrected by Copilot AI
        if not isinstance(maze, list) or not maze or not isinstance(maze[0], list):
            return

        rows = len(maze)
        cols = len(maze[0])
        x, y = self.curr_row, self.curr_col
        direction = self.direction_collection[self.curr_view_id]
        dx, dy = MOVEMENT[direction]
        perp_dx, perp_dy = -dy, dx

        def in_bounds(ix: int, iy: int) -> bool:
            return 0 <= ix < rows and 0 <= iy < cols

        def can_traverse(from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
            if not in_bounds(from_x, from_y) or not in_bounds(to_x, to_y):
                return False

            delta = (to_x - from_x, to_y - from_y)
            if delta == (0, 0):
                return True

            if abs(delta[0]) <= 1 and abs(delta[1]) <= 1:
                if abs(delta[0]) + abs(delta[1]) == 1:
                    wall = MOVEMENT_REV[delta]
                    if wall is None:
                        return False

                    return (
                        maze[from_x][from_y].get(wall, 1) == 0
                        and maze[to_x][to_y].get(OPPOSITE[wall], 1) == 0
                    )

                # diagonal step: require both adjacent cardinal transitions through the corner,
                # including the entry edges on the target diagonal cell.
                orth1 = (from_x + delta[0], from_y)
                orth2 = (from_x, from_y + delta[1])
                return (
                    can_traverse(from_x, from_y, orth1[0], orth1[1])
                    and can_traverse(from_x, from_y, orth2[0], orth2[1])
                    and can_traverse(orth1[0], orth1[1], to_x, to_y)
                    and can_traverse(orth2[0], orth2[1], to_x, to_y)
                )

            return False

        res: list[tuple[int, int]] = []
        for offset in range(-self.vision_range + 1, self.vision_range):
            target_x = x + dx * self.vision_range + perp_dx * offset
            target_y = y + dy * self.vision_range + perp_dy * offset
            ray = list(bresenham(x, y, target_x, target_y))

            connected: list[tuple[int, int]] = []
            for idx, (itx, ity) in enumerate(ray):
                if not in_bounds(itx, ity):
                    break

                if idx == 0:
                    connected.append((itx, ity))
                    continue

                prev_x, prev_y = ray[idx - 1]
                if not can_traverse(prev_x, prev_y, itx, ity):
                    break

                connected.append((itx, ity))

            if connected:
                res.extend(connected)

        self.curr_view_cell = list(dict.fromkeys(res))
    
    def raise_prob(
        self,
        player_pos: tuple[int, int],
        maze: list[list[dict[str, int]]],
        wall_reduction: float = 0.4,
        range_cell: int = 5,
        hiding_cell_reduction: float = 0.6,
    ) -> None:
        wall_reduction = min(1., wall_reduction)
        if wall_reduction < (1 - 0.25)/range_cell:
            wall_reduction = (1 - 0.25)/range_cell
            
        hiding_cell_reduction = min(1., max(hiding_cell_reduction, 0.))
        
        px, py = player_pos
        q = deque([[1., (px, py)]])
        visited = set()
        res = []
        
        while q:
            curr_prob, (curr_x, curr_y) = q.popleft()
            
            if (curr_prob <= 0.25 or (curr_x, curr_y) in visited
                or not (0 <= curr_x < len(maze)) or not (0 <= curr_y < len(maze[0]))):
                continue
            
            visited.add((curr_x, curr_y))
            res.append((curr_x, curr_y, curr_prob))
            
            for key, val in maze[curr_x][curr_y].items():
                prob_reduction = (1 - 0.25)/range_cell
                if val == 1 and key != "hiding":
                    prob_reduction = wall_reduction
                
                if key != "hiding":
                    (dx, dy) = MOVEMENT[key]
                    opposite_wall = OPPOSITE[key]
                    new_x, new_y = curr_x+dx, curr_y+dy
                    if not (0 <= new_x <= len(maze) - 1) or not (0 <= new_y <= len(maze[0]) - 1):
                        continue
                        
                    if maze[new_x][new_y][opposite_wall] == 1 or maze[curr_x][curr_y][key] == 1:
                        prob_reduction = wall_reduction
                else:
                    if val == 1:
                        prob_reduction = hiding_cell_reduction
                    
                if (new_x, new_y) not in visited:
                    q.append([curr_prob - prob_reduction, (new_x, new_y)])
                    
        for (row, col, prob) in res:
            if self.prob_map[row][col] > 0.25:
                new_prob = (self.prob_map[row][col] + prob)/2
            else:
                new_prob = prob
                
            self.prob_map[row][col] = min(1., max(0.25, new_prob))
            
    def decay_prob(
        self,
        d_prob: float,
    ) -> None:
        for i in range(len(self.prob_map)):
            for j in range(len(self.prob_map[0])):
                self.prob_map[i][j] = max(0.25, self.prob_map[i][j] - d_prob)
    
    def update_state(
        self,
        id: int = None,
        state: Literal["chase", "patrol", "suspicious"] = None,
    ) -> None:
        if id is not None and isinstance(id, int) and 0 <= id <= len(self.state_collection) - 1:
            self.curr_state_id = id
            return
        
        if state != self.state_collection[self.curr_state_id] and state in self.state_collection:
            self.curr_state_id = self.state_collection.index(state)
            return
        
    def update_direction(
        self,
        id: int = None,
        direction: Literal["up", "down", "left", "right"] = None
    ) -> None:
        if id is not None and isinstance(id, int) and 0 <= id <= 3:
            self.curr_view_id = id
            return
        
        if direction in self.direction_collection:
            self.curr_view_id = self.direction_collection.index(direction)
            return
        
    def update_hear_player(
        self,
        val: bool,
    ) -> None:
        self.hear_player = val
        
    def update_see_player(
        self,
        val: bool,
    ) -> None:
        self.see_player = val
        
    def move_to(
        self, 
        new_row: int,
        new_col: int,
        maze: list[list[dict[str, int]]],
    ) -> None:
        if new_row is not None and new_col is not None:
            move_direction_change = (new_row - self.curr_row, new_col - self.curr_col)
            move_direction = MOVEMENT_REV.get(move_direction_change, None)
            
            if move_direction:
                self.curr_row = new_row
                self.curr_col = new_col
                self.update_direction(direction=move_direction)
                self.cell_in_view(maze=maze)
                
                for (pos_x, pos_y) in self.curr_view_cell:
                    self.prob_map[pos_x][pos_y] = 0.25
                    if (pos_x, pos_y) not in self.checked_list:
                        self.checked_list.append((pos_x, pos_y))
                
                if len(self.checked_list) > self.max_mem:
                    skip_id = len(self.checked_list) - self.max_mem
                    self.checked_list = self.checked_list[skip_id:]
    
    @property
    def get_speed(self) -> Union[int, float]:
        if self.curr_state_id == 0 or self.curr_state_id == 2:
            return self.walk_speed_mult

        if self.curr_state_id == 1:
            return self.patrol_speed_mult
        
    @property
    def get_curr_cell_in_view(self):
        return self.curr_view_cell
        
    @property
    def get_prob_map(self) -> list[list[float]]:
        return self.prob_map
    
    @property
    def get_checked_list(self) -> list[tuple[int, int]]:
        return self.checked_list
        
    @property
    def get_pos(self) -> tuple[int, int]:
        return (self.curr_row, self.curr_col)
    
    @property
    def get_state_id(self):
        return self.curr_state_id
    
    @property
    def get_state(self):
        return self.state_collection[self.curr_state_id]
    
    @property
    def get_hear_player(self):
        return self.hear_player
    
    @property
    def get_see_player(self):
        return self.see_player