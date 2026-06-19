from hns_maze.generation.dsu import perform_connection as perform_connection_dsu
from hns_maze.generation.generate_grid import create, add_hiding_spot
from hns_maze.generation.flood_fill import perform_connection
import time

def generate(
    rows: int,
    cols: int,
    wall_prob: float = 0.5,
    hiding_prob: float = 0.25,
) -> tuple[list[list[dict[str, int]]], tuple[int], tuple[int]]:
    maze_now = time.time()
    init_maze = create(rows=rows, cols=cols, wall_prob=wall_prob)
    
    connected_maze = perform_connection_dsu(init_maze)
    
    final_maze = add_hiding_spot(grid=connected_maze, hiding_prob=hiding_prob)
    print(f"\n<> Maze generation duration: {((time.time() - maze_now)*1000):.2f} ms")
    
    return final_maze