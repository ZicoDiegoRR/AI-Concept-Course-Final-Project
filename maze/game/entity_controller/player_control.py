from typing import Literal
from .shared_control import *
from ..entity_state.player import Player

player_class = None

def init_player(
    init_row: int,
    init_col: int,
    vision_range: int,
    row_size: int,
    col_size: int,
) -> None:
    global player_class
    
    player_class = Player(
        init_row=init_row,
        init_cols=init_col,
        vision_range=vision_range,
        row_size=row_size,
        col_size=col_size,
    )
    
def move_player(
    maze: list[list[dict[str, int]]],
    move: Literal["up", "down", "left", "right"],
) -> None:
    global player_class
    if player_class is None:
        return
    
    cx, cy = player_class.get_pos
    
    dx, dy = MOVEMENT[move]
    nx, ny = cx+dx, cy+dy
    if not (0 <= nx <= len(maze) - 1 and 0 <= ny <= len(maze[0]) - 1):
        return
    
    opposite_wall = OPPOSITE[move]
    if maze[cx][cy][move] == 0 and maze[nx][ny][opposite_wall] == 0:
        player_class.move_to(nx, ny)
        if maze[nx][ny]["hiding"] == 1:
            player_class.toggle_hiding(True)
        else:
            player_class.toggle_hiding(False)
            
def run_player(
    maze: list[list[dict[str, int]]],
    move: Literal["up", "down", "left", "right", "none"],
    agent_pos: tuple[int, int],
    pressed_movement_toggle: bool,
) -> None:
    global player_class
    if pressed_movement_toggle:
        player_class.toggle_movement()
        
    if move != "none":
        move_player(maze=maze, move=move)
        
    player_see_agent = agent_spotted(
        player_vision=player_class.get_curr_cell_view, 
        agent_pos=agent_pos
    )
    player_class.toggle_see_agent(player_see_agent)
    
def get_player_state() -> dict:
    global player_class
    if player_class is None:
        return None
    
    state_dict = {
        "curr_pos": player_class.get_pos,
        "speed": player_class.get_speed,
        "see_agent": player_class.get_see_agent,
        "hiding": player_class.get_player_hiding,
        "known_map": player_class.get_known_map,
        "vision": player_class.get_curr_cell_view
    }
    return state_dict