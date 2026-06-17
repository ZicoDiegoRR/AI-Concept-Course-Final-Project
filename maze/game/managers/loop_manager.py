from ...generation.generate_all import generate
from ..interface.backbone import clock, FPS
from .game_manager import *
from .ui_manager import *

"""Main loop manager for Hide & Seek.

This module implements UI state transitions, game initialization, and the
main gameplay loop that drives rendering and entity updates.
"""

UI_STATE = ["main_menu", "play_menu", "settings_menu", "gameplay"] 
ui_state_id = 0
initiated_maze = False

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
    "wall_prob": None,
    "hiding_prob": 0.25,
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
    """Run the Hide & Seek game loop.

    The loop handles UI flow, maze generation, entity state initialization,
    rendering, and throttled gameplay updates.
    """
    global ui_state_id, player_dict, agent_dict, game_dict, maze_dict, initiated_maze
    curr_game_state = {
        "maze": None,
        "timer": None,
        "player_pos": None,
        "player_speed": None,
        "player_vision": None,
        "player_color": None,
        "agent_pos": None,
        "agent_speed": None,
        "agent_vision": None,
        "agent_color": None,
    }
    
    curr_visual_dict = {
        "player_vision": None,
        "player_known_map": None,
        "agent_see_player": None,
        "agent_hear_player": None,
        "remaining_time": None,
        "player_walking": None,
        "view_origin": None,
        "player_pos": None,
        "agent_pos": None,
        "maze_grid": None,
        "camera_offset": None,
    }
    
    # AI-generated: throttle gameplay ticks to a fixed interval
    tick_interval = 0.125
    tick_accumulator = 0.0
    frame_dt_accumulate = 0.0
    
    pending_move = "none"
    pending_toggle = False

    running = True
    while running:
        if ui_state_id == 0:
            initiated_maze = False
            reset_game()
            
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
                maze_dict["wall_prob"] = game_rule["wall_prob"]
                timer = game_rule["timer"]
                
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
            if not game_dict["maze"] or not initiated_maze:
                game_dict["maze"] = generate(
                    rows=maze_dict["rows"],
                    cols=maze_dict["cols"],
                    wall_prob=maze_dict["wall_prob"],
                    hiding_prob=maze_dict["hiding_prob"]
                )
                curr_visual_dict["maze_grid"] = game_dict["maze"]
                create_visual(
                    rows=maze_dict["rows"],
                    cols=maze_dict["cols"]
                )
                
                initiated_maze = True

            init_entities(
                player_dict=player_dict,
                agent_dict=agent_dict,
                game_dict=game_dict,
            )
            
            curr_player_state, curr_agent_state = get_entity_states()

            curr_game_state["maze"] = game_dict["maze"]
            curr_game_state["player_pos"] = curr_player_state["curr_pos"]
            curr_game_state["player_speed"] = curr_player_state["speed"]
            curr_game_state["player_vision"] = curr_player_state["vision"]
            curr_game_state["player_color"] = player_dict["color"]
            curr_game_state["agent_pos"] = curr_agent_state["curr_pos"]
            curr_game_state["agent_speed"] = curr_agent_state["speed"]
            curr_game_state["agent_vision"] = curr_agent_state["vision"]
            curr_game_state["agent_color"] = agent_dict["color"]
            curr_game_state["timer"] = timer
            
            curr_visual_dict["player_vision"] = curr_player_state["vision"]
            curr_visual_dict["player_known_map"] = curr_player_state["known_map"]
            curr_visual_dict["agent_see_player"] = curr_agent_state["see_player"]
            curr_visual_dict["agent_hear_player"] = curr_agent_state["hear_player"]
            curr_visual_dict["remaining_time"] = timer
            curr_visual_dict["player_walking"] = curr_player_state["speed"] == 1.
            
            # AI-generated: frame accumulation to determine one second
            frame_per_second = clock.tick(FPS)
            frame_dt = frame_per_second / 1000.0
            tick_accumulator += frame_dt
            frame_dt_accumulate += frame_dt

            # AI-generated: decrement the timer once per full second
            if frame_dt_accumulate >= 1.0:
                seconds = int(frame_dt_accumulate)
                frame_dt_accumulate -= seconds
                timer = max(0, timer - seconds)

            state_dict = render_gameplay(
                game_dict=curr_game_state,
                dt=frame_dt,
            )
            curr_visual_dict["view_origin"] = state_dict["view_origin"]
            curr_visual_dict["player_pos"] = state_dict["player_pos"]
            curr_visual_dict["agent_pos"] = state_dict["agent_pos"]
            curr_visual_dict["camera_offset"] = state_dict["camera_offset"]
            
            render_visual(
                curr_visual_dict, dt=frame_dt_accumulate,
            )
            
            flip_pygame()
            
            # AI-generated: multiple-tick-update handler
            if state_dict["move"] != "none":
                pending_move = state_dict["move"]
            if state_dict["pressed_movement_toggle"]:
                pending_toggle = True

            ui_state_id = state_dict["state"]
            
            # AI-assisted: interpolate the entity movement based on tick
            if tick_accumulator >= tick_interval:
                tick_accumulator -= tick_interval
                run_entities(
                    player_move=pending_move,
                    pressed_movement_toggle=pending_toggle,
                    agent_still_moving=state_dict["agent_moving"]
                )
                pending_move = "none"
                pending_toggle = False
            
        if ui_state_id == -1:
            running = False