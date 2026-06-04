from .game_manager import init_entities, run_entities
from ...generation.generate_all import generate
from .ui_manager import render

UI_STATE = ["main_menu", "play_menu", "settings_menu", "gameplay"] 
ui_state_id = 0
timer = None

game_dict = {
    "prob_decay": None,
    "wall_reduction": None,
    "hiding_cell_reduction": None,
    "range_raise_prob": None,
    "maze": None,
}

player_dict = {
    "vision_range": None,
    "color": (0, 255, 0),
}

agent_dict = {
    "vision_range": None,
    "color": (255, 0, 0),
    "h_func_init": "Euclidean",
    "max_mem": None,
}

def play_hns():
    running = True
    while running:
        continue
    
    # TODO