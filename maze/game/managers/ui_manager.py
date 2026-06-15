from ..interface import main_menu, settings_menu, play_menu, maze_gameplay
from typing import Any

game_state_ui = maze_gameplay.MazeRenderer()

def render_main_menu() -> dict[str, int]:
    state_dict = main_menu.main_menu()
    return state_dict

def render_settings_menu(init_state=None) -> dict:
    state_dict = settings_menu.settings_menu(init_state=init_state)
    return state_dict

def render_play_menu() -> dict:
    state_dict = play_menu.play_menu()
    return state_dict

def render_gameplay(game_dict: dict[str, Any], dt: float) -> dict:
    state_dict = game_state_ui.update(game_dict, dt)
    return state_dict