from collections import deque
from .shared import *

class Player:
    def __init__(
        self, 
        init_row: int, 
        init_cols: int,
        vision_range: int, 
        
        row_size: int,
        col_size: int,
        color: tuple[int, int, int] = (0, 255, 0),
    ):
        self.curr_row = init_row
        self.curr_col = init_cols
        self.color_rgb = color
        
        self.spot_agent = False
        self.is_hiding = False
        self.is_walking = True
        self.walk_speed_mult = 1
        self.sneak_speed_mult = 0.5
        
        self.vision_range = vision_range
        self.known_map = [[False for _ in range(col_size)] for _ in range(row_size)]
        self.curr_view_cell = []
    
    def cell_in_view(
        self, 
        maze: list[list[dict[str, int]]],
    ) -> list[tuple[int, int]]:
        if not isinstance(maze, list):
            return
        
        if not isinstance(maze[0], list):
            return
        
        q = deque([[0, (self.curr_row, self.curr_col)]])
        visited = set()
        res = []
        movement = MOVEMENT
        opposite = OPPOSITE
        
        while q:
            curr_step, (curr_x, curr_y) = q.popleft()
            
            if curr_step >= self.vision_range or (curr_x, curr_y) in visited:
                continue
            
            visited.add((curr_x, curr_y))
            res.append((curr_x, curr_y))
            for key, val in maze[curr_x][curr_y].items():
                if val == 0:
                    (dx, dy) = movement[key]
                    opposite_wall = opposite[key]
                    new_x, new_y = curr_x+dx, curr_y+dy
                    if not 0 <= new_x <= len(maze) - 1 or not 0 <= new_y <= len(maze[0]) - 1:
                        continue
                    
                    if maze[new_x][new_y][opposite_wall] == 0 and (new_x, new_y) not in visited:
                        q.append([curr_step+1, (new_x, new_y)])
                  
        self.curr_view_cell = res
        for (cx, cy) in res:
            self.known_map[cx][cy] = True
    
    def propagate_noise(
        self,
        maze: list[list[dict[str, int]]],
        wall_reduction: int = 2,
        range_cell: int = 5,
    ) -> list[tuple[int, int]]:
        if not self.is_walking:
            return []
        
        if wall_reduction <= 0:
            print("WARN: The reduction wall value is invalid. Setting it to 1 instead...")
            wall_reduction = 1
        
        q = deque([[range_cell, (self.curr_row, self.curr_col)]])
        visited = set()
        res = []
        movement = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1),
        }
        opposite = {
            "up": "down",
            "down": "up",
            "left": "right",
            "right": "left",
        }
        
        while q:
            curr_noise, (curr_x, curr_y) = q.popleft()
            
            if curr_noise <= 0 or (curr_x, curr_y) in visited:
                continue
            
            visited.add((curr_x, curr_y))
            res.append((curr_x, curr_y))
            for key, val in maze[curr_x][curr_y].items():
                noise_reduction = 1
                if val == 1:
                    noise_reduction = wall_reduction
                    
                (dx, dy) = movement[key]
                opposite_wall = opposite[key]
                new_x, new_y = curr_x+dx, curr_y+dy
                if not (0 <= new_x <= len(maze) - 1) or not (0 <= new_y <= len(maze[0]) - 1):
                    continue
                    
                if maze[new_x][new_y][opposite_wall] == 1:
                    noise_reduction = wall_reduction
                    
                if (new_x, new_y) not in visited:
                    q.append([curr_noise - noise_reduction, (new_x, new_y)])
                    
        return res
        
    def move_to(
        self, 
        maze: list[list[dict[str, int]]],
        new_row: int,
        new_col: int,
    ) -> None:
        if new_row is not None and new_col is not None:
            self.curr_row = new_row
            self.curr_col = new_col
            
            self.cell_in_view(maze)

    def toggle_movement(self):
        self.is_walking = not self.is_walking
        
    def toggle_hiding(
        self,
        val: bool,
    ) -> None:
        self.is_hiding = val
        
    def toggle_see_agent(
        self,
        see: bool
    ) -> None:
        self.spot_agent = see
        
    @property
    def get_speed(self) -> float:
        if self.is_walking:
            return self.walk_speed_mult
        else:
            return self.sneak_speed_mult
        
    @property
    def get_pos(self) -> tuple[int, int]:
        return (self.curr_row, self.curr_col)
    
    @property
    def get_curr_cell_view(self):
        return self.curr_view_cell
    
    @property
    def get_known_map(self):
        return self.known_map
    
    @property
    def get_see_agent(self):
        return self.spot_agent
    
    @property
    def get_player_hiding(self):
        return self.is_hiding