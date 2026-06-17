from hns_maze.game.interface import main_menu, settings_menu, play_menu, maze_gameplay, visual
from typing import Any
import pygame

game_state_ui = maze_gameplay.MazeRenderer()
visual_state = None

def render_main_menu() -> dict[str, int]:
    global visual_state
    visual_state = None
    
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

def create_visual(
    rows: int,
    cols: int,
) -> None:
    global visual_state
    visual_state = visual.create_visual_effects(cols=cols, rows=rows)

def render_visual(visual_dict: dict[str, Any], dt: float) -> None:
    visual_state.update(visual_dict, dt=dt)
    visual_state.draw(visual_dict)
    
def flip_pygame() -> None:
    pygame.display.flip()