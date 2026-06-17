MOVEMENT = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

MOVEMENT_REV = {
    (-1, 0): "up",
    (1, 0): "down",
    (0, -1): "left",
    (0, 1): "right",
}

OPPOSITE = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left",
}

def player_spotted(
    player_pos: tuple[int, int], 
    agent_vision: list[tuple[int, int]],
) -> bool:
    return player_pos in agent_vision

def agent_heard(
    noise_propagation: list[tuple[int, int]],
    agent_pos: tuple[int, int],
) -> bool:
    return agent_pos in noise_propagation

def agent_spotted(
    player_vision: list[tuple[int, int]],
    agent_pos: tuple[int, int]
) -> bool:
    return agent_pos in player_vision

def agent_raised_prob(
    prob_map: list[list[float]],
) -> bool:
    return any(any(col for col in row if col > 0.25) for row in prob_map)

def agent_notice_player_before_disappear(
    player_pos: tuple[int, int],
    agent_vision: list[tuple[int, int]],
    maze: list[list[dict[str, int]]],
) -> bool:
    px, py = player_pos
    
    for (ax, ay) in agent_vision:
        d_to_player = (px-ax, py-ay)
        move = MOVEMENT_REV.get(d_to_player, None)
        
        if move:
            wall = move
            opposite_wall = OPPOSITE[wall]
            if maze[ax][ay][wall] == 0 and maze[px][py][opposite_wall] == 0:
                return True
            
    return False