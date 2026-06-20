from hns_maze.algorithm.heuristics import euclidean, manhattan
from hns_maze.game.entity_state.agent import Agent
from hns_maze.algorithm import a_star, bfs
from hns_maze.game.entity_controller.shared_control import *
from collections import deque
from typing import Callable
import heapq

agent_class = None
h_func = None
curr_agent_path = deque([])

def init_agent(
    init_row: int, 
    init_cols: int,
    vision_range: int, 
    row_size: int,
    col_size: int,
    h_func_init: Callable,
    max_cell_mem: int,
    color: tuple[int, int, int] = (255, 0, 0),
) -> None:
    global agent_class, h_func
    
    h_func = euclidean.compute if h_func_init == "Euclidean" else manhattan.compute
    agent_class = Agent(
        init_row=init_row,
        init_cols=init_cols,
        vision_range=vision_range,
        row_size=row_size,
        col_size=col_size,
        color=color,
        max_cell_mem=max_cell_mem
    )
    
def patrol_find(
    maze: list[list[dict[str, int]]],
    hiding_cell_reduction: float,
) -> None:
    global agent_class, curr_agent_path
    if agent_class is None or agent_class.get_state != "patrol":
        return
    
    visited_mem = agent_class.get_checked_list
    curr_pos = agent_class.get_pos
    
    path_to_new = bfs.solve(
        grid=maze, visited=visited_mem, 
        start=curr_pos, 
        hiding_cell_reduction=hiding_cell_reduction
    )
    curr_agent_path = deque(path_to_new)
    
def suspicious_find(
    maze: list[list[dict[str, int]]],
) -> None:
    global agent_class, curr_agent_path, h_func
    if agent_class is None or agent_class.get_state != "suspicious":
        return
    
    curr_pos = agent_class.get_pos
    prob_map = agent_class.get_prob_map
    
    raised_prob_cell = []
    for i in range(len(prob_map)):
        for j in range(len(prob_map[0])):
            if (i, j) != agent_class.get_pos and prob_map[i][j] > 0.25: # By design
                heapq.heappush(raised_prob_cell, 
                    (
                        h_func(agent_class.get_pos, (i, j)),
                        -prob_map[i][j], i, j
                    )
                )
                
    if not raised_prob_cell:
        return
    
    to_check = list(raised_prob_cell[0])[2:]
    
    path_to_site = a_star.solve(
        grid=maze, start=curr_pos, 
        goal=tuple(to_check), h_func=h_func
    )
    curr_agent_path = deque(path_to_site)
    
def chase_find(
    maze: list[list[dict[str, int]]],
    player_pos: tuple[int, int],
    exclude_start: bool,
) -> None:
    global agent_class, curr_agent_path, h_func
    if agent_class is None or agent_class.get_state != "chase":
        return
    
    curr_pos = agent_class.get_pos
    path_to_target = a_star.solve(
        grid=maze, start=curr_pos, 
        goal=player_pos, h_func=h_func
    )
    curr_agent_path = deque(path_to_target[1 if exclude_start else 0:])
    
def move_agent(
    maze: list[list[dict[str, int]]],
) -> None:
    global agent_class, curr_agent_path
    if agent_class is None or not curr_agent_path:
        return
    
    nxt_x, nxt_y = curr_agent_path.popleft()
    agent_class.move_to(new_row=nxt_x, new_col=nxt_y, maze=maze)
    
def decay_prob(d_prob: float) -> None:
    global agent_class
    
    if curr_agent_path:
        agent_class.decay_prob(d_prob)
    
def run_agent(
    maze: list[list[dict[str, int]]],
    player_pos: tuple[int, int],
    player_noise: list[tuple[int, int]],
    hiding_timer_run_out: bool,
    wall_reduction: float,
    hiding_cell_reduction: float,
    range_raise_prob: int,
    prob_decay: float,
    agent_must_move: bool = True,
) -> None:
    global agent_class, curr_agent_path, h_func
    if agent_class is None:
        raise ValueError("Agent class can't be None.")
    
    curr_pos = agent_class.get_pos
    
    # Get chase check
    agent_spot_player = bool(
        player_spotted(player_pos, agent_class.get_curr_cell_in_view)
        or hiding_timer_run_out
    )
    agent_notice_player_disappear = agent_notice_player_before_disappear(
        player_pos, agent_class.get_curr_cell_in_view, maze
    )
    
    agent_class.update_see_player(agent_spot_player)
    
    # Sees player or in "chase" mode and either noticing player before disappearing or still trying to chase
    if agent_spot_player or (
        agent_class.get_state == "chase" and (
            curr_agent_path 
            or agent_notice_player_disappear
        )
    ):
        agent_class.update_state(state="chase")
        if agent_spot_player or agent_notice_player_disappear:
            chase_find(maze=maze, player_pos=player_pos, exclude_start=True)
        if agent_must_move: move_agent(maze=maze)
        return
    
    # In "chase" mode but has nowhere to go
    elif agent_class.get_state == "chase" and not curr_agent_path:
        agent_class.update_state(state="suspicious")
        
        possible_path_to_player = a_star.solve(
            grid=maze, start=agent_class.get_pos, 
            goal=player_pos, h_func=h_func
        )
        dist_to_player = manhattan.compute(player_pos, agent_class.get_pos)
        truncate_path = min(
            dist_to_player,
            len(possible_path_to_player)
        ) if dist_to_player >= 3 else len(possible_path_to_player)
        possible_path = possible_path_to_player[:truncate_path]
        
        for pos in possible_path:
            agent_class.raise_prob(
                player_pos=pos, 
                maze=maze, 
                wall_reduction=wall_reduction, 
                range_cell=range_raise_prob, 
                hiding_cell_reduction=hiding_cell_reduction
            )
            
        return
    
    # Get suspicious check        
    agent_heard_player = agent_heard(player_noise, curr_pos)
    raised_prob_map = agent_raised_prob(agent_class.get_prob_map)
    
    agent_class.update_hear_player(agent_heard_player)

    # Hears something or in "suspicious" mode 
    if agent_heard_player or agent_class.get_state == "suspicious" or raised_prob_map:
        agent_class.update_state(state="suspicious")
        
        # If hears player
        if agent_heard_player: 
            agent_class.raise_prob(
                player_pos=player_pos,
                maze=maze,
                wall_reduction=wall_reduction,
                range_cell=range_raise_prob,
                hiding_cell_reduction=hiding_cell_reduction
            )
        
        # If the path is still undefined
        any_path = bool(curr_agent_path)
        if not any_path: 
            suspicious_find(maze=maze)
            any_path = bool(curr_agent_path)
            
        # If there's still no path generated or no raised probability
        if not any_path:
            agent_class.update_state(state="patrol")
            return
        
        if agent_must_move: move_agent(maze=maze)
        return
    
    # Patrol
    if curr_agent_path:
        if agent_must_move: move_agent(maze=maze)
    else:
        patrol_find(maze=maze, hiding_cell_reduction=hiding_cell_reduction)
        
    return

def get_agent_state() -> dict:
    if agent_class is None:
        return None
    
    state_dict = {
        "curr_pos": agent_class.get_pos,
        "behavior": agent_class.get_state,
        "speed": agent_class.get_speed,
        "vision": agent_class.get_curr_cell_in_view,
        "prob_map": agent_class.get_prob_map,
        "hear_player": agent_class.get_hear_player,
        "see_player": agent_class.get_see_player,
    }
    return state_dict