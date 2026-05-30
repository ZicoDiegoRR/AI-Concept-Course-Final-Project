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
        self.patrol_speed_mult = 0.7
        
        self.direction_collection = ["up", "down", "left", "right"]
        self.curr_view_id = random.choice(self.direction_collection)
        self.curr_view_cell = []
        
        self.prob_map = [[0.25 for _ in range(col_size)] for _ in range(row_size)]
        self.checked_list = [(self.curr_row, self.curr_col)]
        self.max_mem = max_cell_mem

    def cell_in_view(
        self,
        maze: list[list[dict[str, int]]],
    ) -> None:
        if not isinstance(maze, list):
            return None
        
        if not isinstance(maze[0], list):
            return None

        move = MOVEMENT[self.curr_view_id]
        widen_move = tuple(1 if item == 0 else 0 for item in move)
        
        x, y = self.curr_row, self.curr_col
        dx, dy = widen_move
            
        widen_area_tile = []
        for i in range(-self.vision_range+1, self.vision_range):            
            new_x = x + self.vision_range + (dx * i) if dx == 1 else x + self.vision_range
            new_y = y + self.vision_range + (dy * i) if dy == 1 else y + self.vision_range
            
            widen_area_tile.append((new_x, new_y))
            
        res = []
        for (wx, wy) in widen_area_tile:
            intersect_tile = list(bresenham(x, y, wx, wy))[::-1]
            connected = []
            
            for i, (itx, ity) in enumerate(intersect_tile):
                if not (0 <= itx < len(maze)) or not (0 <= ity < len(maze[0])):
                    continue
                
                if (itx, ity) == (x, y) or i == len(intersect_tile) - 1:
                    connected.append((itx, ity))
                
                nxt_x, nxt_y = intersect_tile[i+1]
                dx_from_next = itx - nxt_x
                dy_from_next = ity - nxt_y
                which_changed = (dx_from_next, dy_from_next)
                
                wall_to_check = []
                if which_changed[0] == 1:
                    wall_to_check.append("up")
                elif which_changed[0] == -1:
                    wall_to_check.append("down")
                    
                if which_changed[1] == 1:
                    wall_to_check.append("left")
                elif which_changed[1] == -1:
                    wall_to_check.append("right")
                    
                no_wall = True
                for wall in wall_to_check:
                    opposite_wall = OPPOSITE[wall]
                    neighx, neighy = MOVEMENT[opposite_wall]
                    newx, newy = itx+neighx, ity+neighy
                    
                    wall_move = MOVEMENT[wall]
                    nxt_neighx, nxt_neighy = nxt_x+wall_move[0], nxt_y+wall_move[1]
                    if (
                        (maze[itx][ity][wall] == 1) 
                        or (maze[newx][newy][opposite_wall] == 1)
                        or (maze[nxt_x][nxt_y][opposite_wall] == 1)
                        or (maze[nxt_neighx][nxt_neighy][wall] == 1)
                    ):
                        no_wall = False
                        connected.clear()
                        break
                        
                if no_wall:
                    connected.append((itx, ity))
                        
            if connected:
                res.extend(connected)
                    
        res_final = list(set(res))
        self.curr_view_cell = res_final
    
    def raise_prob(
        self,
        player_pos: tuple[int, int],
        maze: list[list[dict[str, int]]],
        wall_reduction: float = 0.4,
        range_cell: int = 5,
    ) -> None:
        if wall_reduction <= (1 - 0.25)/range_cell or wall_reduction > 1.:
            print("WARN: The reduction wall value is invalid. Setting it to 0.4 (default) instead...")
            wall_reduction = 0.4
        
        px, py = player_pos
        q = deque([[1, (px, py)]])
        visited = set()
        res = []
        
        while q:
            curr_prob, (curr_x, curr_y) = q.popleft()
            
            if curr_prob <= 0.25 or (curr_x, curr_y) in visited:
                continue
            
            visited.add((curr_x, curr_y))
            res.append((curr_x, curr_y, curr_prob))
            
            for key, val in maze[curr_x][curr_y].items():
                prob_reduction = (1 - 0.25)/range_cell
                if val == 1:
                    prob_reduction = wall_reduction
                    
                (dx, dy) = MOVEMENT[key]
                opposite_wall = OPPOSITE[key]
                new_x, new_y = curr_x+dx, curr_y+dy
                if not (0 <= new_x <= len(maze) - 1) or not (0 <= new_y <= len(maze[0]) - 1):
                    continue
                    
                if maze[new_x][new_y][opposite_wall] == 1:
                    prob_reduction = wall_reduction
                    
                if (new_x, new_y) not in visited:
                    q.append([curr_prob - prob_reduction, (new_x, new_y)])
                    
        for (row, col, prob) in res:
            self.prob_map[row][col] = prob
            
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
        if id is not None and isinstance(id, int) and 0 <= id <= 2:
            self.curr_state_id = id
            return
        
        if state in self.state_collection:
            self.curr_state_id = self.direction_collection.index(state)
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
        
    def move_to(
        self, 
        new_row: int,
        new_col: int,
        maze: list[list[dict[str, int]]],
    ) -> None:
        if new_row is not None and new_col is not None:
            move_direction_change = (new_row - self.curr_row, new_col - self.curr_col)
            move_direction = MOVEMENT_REV[move_direction_change]
            
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