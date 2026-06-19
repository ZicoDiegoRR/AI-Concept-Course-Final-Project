from hns_maze.game.entity_controller import player_control, agent_control
from hns_maze.game.entity_spawning.spawn_handler import spawn_entities
from typing import Literal

# Updatable values
last_player_state = None
last_agent_state = None
player_hiding_timer = float("inf")

# Non-updatable values (gameplay settings)
prob_decay = None
wall_reduction = None
hiding_cell_reduction = None
range_raise_prob = None
maze = None
initialized = False

def init_entities(
    player_dict: dict,
    agent_dict: dict,
    game_dict: dict
) -> None:
    global wall_reduction, hiding_cell_reduction, range_raise_prob, initialized
    global last_agent_state, last_player_state, prob_decay, maze
    
    if not initialized:
        maze = game_dict["maze"]
        row_size, col_size = len(maze), len(maze[0])
        
        prob_decay = game_dict["prob_decay"]
        wall_reduction = game_dict["wall_reduction"]
        hiding_cell_reduction = game_dict["hiding_cell_reduction"]
        range_raise_prob = game_dict["range_raise_prob"]
        
        (p_init_row, p_init_col), (a_init_row, a_init_col) = spawn_entities(maze=maze)
        
        p_vision_range = player_dict["vision_range"]
        p_color = player_dict["color"]

        a_vision_range = agent_dict["vision_range"]
        a_h_func_init = agent_dict["h_func_init"]
        a_max_mem = int(agent_dict["max_mem"] * (row_size/10 * col_size/10))
        a_color = agent_dict["color"]
        
        player_control.init_player(
            init_row=p_init_row,
            init_col=p_init_col,
            vision_range=p_vision_range,
            row_size=row_size,
            col_size=col_size,
            color=p_color
        )
        
        agent_control.init_agent(
            init_row=a_init_row,
            init_cols=a_init_col,
            vision_range=a_vision_range,
            row_size=row_size,
            col_size=col_size,
            h_func_init=a_h_func_init,
            max_cell_mem=a_max_mem,
            color=a_color
        )
        
        player_control.vision_init(maze)
        
        last_agent_state = agent_control.get_agent_state()
        last_player_state = player_control.get_player_state()
        
        initialized = True
    
def run_entities(
    player_move: Literal["up", "down", "left", "right", "none"],
    pressed_movement_toggle: bool,
    agent_still_moving: bool,
) -> tuple[dict, dict]:
    global player_hiding_timer, last_agent_state, last_player_state
    
    agent_pos = last_agent_state["curr_pos"]
    
    player_control.run_player(
        move=player_move, agent_pos=agent_pos, 
        pressed_movement_toggle=pressed_movement_toggle,
        wall_reduction=wall_reduction/range_raise_prob, 
        range_noise_prop=range_raise_prob, maze=maze,
    )
    
    hiding_timer_runs_out = False
    curr_player_state = player_control.get_player_state()
    if curr_player_state["hiding"]:
        if player_hiding_timer == float("inf"):
            player_hiding_timer = 60
        elif player_hiding_timer <= 0:
            player_hiding_timer = 60
            hiding_timer_runs_out = True
    else:
        player_hiding_timer = float("inf")
        
    player_pos = curr_player_state["curr_pos"]
    player_noise = curr_player_state["player_noise"]
    
    if not agent_still_moving:
        agent_must_move = True
    else:
        agent_must_move = False

    agent_control.run_agent(
        maze=maze, player_pos=player_pos, 
        player_noise=player_noise, 
        hiding_timer_run_out=hiding_timer_runs_out, 
        wall_reduction=wall_reduction, 
        hiding_cell_reduction=hiding_cell_reduction, 
        range_raise_prob=range_raise_prob, prob_decay=prob_decay,
        agent_must_move=agent_must_move,
    )
    curr_agent_state = agent_control.get_agent_state()
    
    agent_pos = curr_agent_state["curr_pos"]
    player_control.vision_update(agent_pos=agent_pos)
    
    last_agent_state, last_player_state = curr_agent_state, curr_player_state
    
    player_control.reset_noise()
    return get_entity_states()

def decrement_hiding_timer(decrement: int = 1) -> None:
    global player_hiding_timer
    
    player_hiding_timer = max(0, player_hiding_timer - decrement)
    
def decay_agent_prob() -> None:
    agent_control.decay_prob(prob_decay)

def get_entity_states() -> tuple[dict, dict]:    
    return last_player_state, last_agent_state

def reset_game() -> None:
    global initialized
    
    initialized = False