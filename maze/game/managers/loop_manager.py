from .game_manager import init_entities, run_entities
from ...generation.generate_all import generate
from .ui_manager import *

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
    global ui_state_id, player_dict, agent_dict, game_dict
    
    running = True
    while running:
        if ui_state_id == 0:
            state_dict = render_main_menu()
            
            next_state = state_dict["next_state"]
            ui_state_id = next_state
            
        if ui_state_id == 1:
            running = False
            print("Not implemented")
            # TODO
            
        if ui_state_id == 2:
            init_state = {
                "player_color": player_dict["color"],
                "agent_color": agent_dict["color"],
                "agent_heuristic": agent_dict["h_func_init"],
            }
            
            state_dict = render_settings_menu(init_state=init_state)
            settings_dict = state_dict["settings_dict"]
            
            player_color = settings_dict["player_color"]
            agent_color = settings_dict["agent_color"]
            agent_h_func = settings_dict["agent_heuristic"]
            
            player_dict["color"] = player_color
            agent_dict["color"] = agent_color
            agent_dict["h_func_init"] = agent_h_func
            ui_state_id = state_dict["state"]
            
            print("\nReceived settings:")
            print("- Player color (RGB):", player_dict["color"]) 
            print("- Agent color (RGB):", agent_dict["color"])
            print("- Agent heuristic function:", agent_dict["h_func_init"])
            
        if ui_state_id == 3:
            running = False
            print("Not implemented")
            # TODO
            
        if ui_state_id == -1:
            running = False