from .generate_grid import create, add_hiding_spot
from .flood_fill import perform_connection

def generate(
    rows: int,
    cols: int,
    wall_prob: float = 0.5,
    hiding_prob: float = 0.25,
) -> tuple[list[list[dict[str, int]]], tuple[int], tuple[int]]:
    init_maze = create(rows=rows, cols=cols, wall_prob=wall_prob)
    
    connected_maze = perform_connection(init_maze)
    
    final_maze = add_hiding_spot(grid=connected_maze, hiding_prob=hiding_prob)
    
    return final_maze