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

maze_dict = {
    "rows": None,
    "cols": None,
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
    global ui_state_id, player_dict, agent_dict, game_dict, maze_dict
    
    running = True
    while running:
        if ui_state_id == 0:
            state_dict = render_main_menu()
            
            next_state = state_dict["next_state"]
            ui_state_id = next_state
            
        if ui_state_id == 1:
            state_dict = render_play_menu()
            ui_state_id = state_dict["state"]
            
            player_rule = state_dict["player_dict"]
            agent_rule = state_dict["agent_dict"]
            game_rule = state_dict["game_dict"]
            
            if player_rule and agent_rule and game_rule:
                game_dict["hiding_cell_reduction"] = game_rule["hiding_cell_reduction"]
                game_dict["prob_decay"] = game_rule["prob_decay"]
                game_dict["range_raise_prob"] = game_rule["range_raise_prob"]
                game_dict["wall_reduction"] = game_rule["wall_reduction"]
                
                agent_dict["max_mem"] = game_rule["max_mem"]
                agent_dict["vision_range"] = agent_rule["vision_range"]
                
                player_dict["vision_range"] = player_rule["vision_range"]
                
                maze_dict["rows"] = game_rule["row_size"]
                maze_dict["cols"] = game_rule["col_size"]
                
                print("\nSet gamerules:")
                for dict_item in [game_dict, agent_dict, player_dict, maze_dict]:
                    prefix = '- '
                    if dict_item == agent_dict: prefix = "- agent "
                    elif dict_item == player_dict: prefix = "- player "
                    elif dict_item == maze_dict: prefix = "- maze "
                    for key, val in dict_item.items():
                        if val is not None:
                            print(f"{prefix}{key}: {val}")
            
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