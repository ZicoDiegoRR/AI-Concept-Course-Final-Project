import copy
import random

def add(
    grid: list[list[dict[str, int]]],
    start: tuple[int, int] = None,
    goal: tuple[int, int] = None,
) -> tuple[tuple[int, int], tuple[int,int], list[tuple[int, int]]]:    
    if not start:
        start = (random.randint(1, len(grid) - 2), random.randint(1, len(grid[0]) - 2))

    if not goal:
        goal_x = random.randint(0, len(grid) - 1)
        if goal_x == 0 or goal_x == len(grid) - 1:
            goal_y = random.randint(1, len(grid[0]) - 2)
        else:
            goal_y = random.choice([0, len(grid[0]) - 1])
            
        goal = (goal_x, goal_y)
    
    q = [[goal, [goal]]]
    visited = set()
    step = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while q:
        (cx, cy), path = q.pop()
        
        if (cx, cy) == start:
            return start, goal, path
        
        if (cx, cy) in visited: continue

        visited.add((cx, cy))
        
        new_nodes = []
        selected_move = random.sample(step, k=4)
        for (x, y) in selected_move:
            coor_x, coor_y = cx + x, cy + y
            if (0 <= coor_x <= len(grid) - 1 and 0 <= coor_y <= len(grid[0]) - 1
            ) and (coor_x, coor_y) not in visited:
                
                new_path = path + [(coor_x, coor_y)]
                new_nodes.append([(coor_x, coor_y), new_path])
                
        random.shuffle(new_nodes)
        q.extend(new_nodes)
                
    return start, goal, None

def apply_to_grid_from_goal(
    grid: list[list[dict[str, int]]],
    path: list[tuple[int, int]],
) -> list[list[dict[str, int]]]:
    curr = path[0]
    init_x, init_y = curr
    
    grid_copy = copy.deepcopy(grid)
    if init_x == 0: 
        grid_copy[init_x][init_y]["up"] = 0
    elif init_x == len(grid) - 1: 
        grid_copy[init_x][init_y]["down"] = 0
    elif init_y == 0: 
        grid_copy[init_x][init_y]["left"] = 0
    elif init_y == len(grid[0]) - 1: 
        grid_copy[init_x][init_y]["right"] = 0
            
    opposite = {
        "up": "down", "down": "up",
        "left": "right", "right": "left"
    }
    moves = {
        (-1, 0): "up",
        (1, 0): "down",
        (0, -1): "left",
        (0, 1): "right"
    }
    
    for (x, y) in path[1:]:
        curr_x, curr_y = curr
        
        dx, dy = x - curr_x, y - curr_y
        movement = moves[(dx, dy)]
        opposite_move = opposite[movement]
        
        grid_copy[curr_x][curr_y][movement] = 0
        grid_copy[x][y][opposite_move] = 0
        
        curr = (x, y)
        
    return grid_copy

if __name__ == "__main__":
    def print_maze(grid: list[list[dict[str, int]]]) -> None:
        for row in grid:
            for col in row:
                print("|" if col["left"] else " ", end="")
                if col["up"] and col["down"]:
                    print("ニ", end="")
                elif col["up"]:
                    print("‾", end="")
                elif col["down"]:
                    print("_", end="")
                else:
                    print(" ", end="")
                print("|" if col["right"] else " ", end="")
            print()
    
    grid = [[{'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 0, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}], [{'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 0, 'left': 0, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}], [{'up': 1, 'down': 0, 'left': 1, 'right': 1}, {'up': 1, 'down': 0, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 0, 'left': 1, 'right': 1}, {'up': 1, 'down': 0, 'left': 1, 'right': 1}], [{'up': 0, 'down': 1, 'left': 1, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 0, 'down': 1, 'left': 0, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 1}], [{'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 0, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 0, 'left': 1, 'right': 1}], [{'up': 1, 'down': 0, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 0, 'down': 1, 'left': 0, 'right': 0}, {'up': 1, 'down': 0, 'left': 0, 'right': 1}, {'up': 0, 'down': 0, 'left': 1, 'right': 1}], [{'up': 0, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 1}]]
    print_maze(grid)  
    print()
    
    start, goal, path = add(grid)
    print(apply_to_grid_from_goal(grid, path))
    print(path, start, goal)