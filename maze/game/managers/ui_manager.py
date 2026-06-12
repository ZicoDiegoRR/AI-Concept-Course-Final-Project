from ..interface import main_menu, settings_menu

def render_main_menu() -> dict[str, int]:
    state_dict = main_menu.main_menu()
    return state_dict

def render_settings_menu(init_state=None) -> dict:
    state_dict = settings_menu.settings_menu(init_state=init_state)
    return state_dict