from .create_solution import *
from .generate_grid import create

def generate(
    rows: int,
    cols: int,
    wall_prob: float = 0.5,
) -> tuple[list[list[dict[str, int]]], tuple[int], tuple[int]]:
    init_maze = create(
        rows=rows, cols=cols, wall_prob=wall_prob
    )
    
    start, goal, path = add(init_maze)
    if path is None:
        print("ERR: Failed to add solution to the maze.")
        return None, None, None
    
    new_maze = apply_to_grid_from_goal(
        grid=init_maze, path=path
    )
    
    print(new_maze)
    
    return start, goal, new_maze