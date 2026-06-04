import random
import math

QUADRANT_OPPOSITE = {
    1: 4,
    2: 3,
    3: 2,
    4: 1,
}

def spawn_entities(
    maze: list[list[dict[str, int]]]
) -> list[tuple[int, int]]:
    rows, cols = len(maze), len(maze[0])
    half_row, half_col = int(rows/2), int(cols/2)
    
    quadrant = random.randint(1, 4)
    spawn_loc = []
    
    for it in range(2):
        if it == 1:
            quadrant = QUADRANT_OPPOSITE[quadrant]
            
        x_lower = None
        x_upper = None
        y_lower = None
        y_upper = None
        
        if quadrant == 1:
            x_lower = 0
            x_upper = half_row
            y_lower = 0
            y_upper = half_col
            
        elif quadrant == 2:
            x_lower = half_row+1
            x_upper = rows - 1
            y_lower = 0
            y_upper = half_col
            
        elif quadrant == 3:
            x_lower = half_row+1
            x_upper = rows - 1
            y_lower = half_col+1
            y_upper = cols - 1
            
        elif quadrant == 4:
            x_lower = 0
            x_upper = half_row
            y_lower = half_col+1
            y_upper = cols - 1
            
        x_spawn = random.randint(x_lower, x_upper)
        y_spawn = random.randint(y_lower, y_upper)
        spawn_loc.append((x_spawn, y_spawn))
        
    return spawn_loc