import random

MOVES = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1)
}

OPPOSITE = {
    "up": "down", "down": "up",
    "left": "right", "right": "left"
}

def create(
    rows: int,
    cols: int,
    wall_prob: float = 0.5,
) -> list[list[dict[str, int]]]:
    grid = [[{"up": 0, "down": 0, "left": 0,"right": 0, "hiding": 0} for _ in range(cols)] for _ in range(rows)]

    for i, row  in enumerate(grid):
        for j, col in enumerate(row):
            if i == 0: col["up"] = 1
            elif i == len(grid) - 1: col["down"] = 1
            
            if j == 0: col["left"] = 1
            elif j == len(grid[0]) - 1: col["right"] = 1
            
            no_walls = [key for key, val in col.items() if val == 0 and key != "hiding"]
            if len(no_walls) >= 2:
                num_add_walls = random.randint(1, len(no_walls) - 1)
                select_walls = random.sample(no_walls, k=num_add_walls)
                
                for wall in select_walls:
                    if random.random() <= wall_prob:
                        col[wall] = 1
                        
                        dx, dy = MOVES[wall]
                        adj_wall = OPPOSITE[wall]
                        
                        adj_x, adj_y = i+dx, j+dy
                        grid[adj_x][adj_y][adj_wall] = 1
                        
    for i, row in enumerate(grid):
        for j, col in enumerate(row):
            walls = [key for key, val in col.items() if val == 1]
            if len(walls) == 4:
                banned_key = []
                if i == 0:
                    banned_key.append("up")
                elif i == len(grid) - 1:
                    banned_key.append("down")
                    
                if j == 0:
                    banned_key.append("left")
                elif j == len(grid[0]) - 1:
                    banned_key.append("right")
                    
                potential_no_wall = [key for key in walls if key not in banned_key]
                num_remove_wall = random.randint(1, 2)
                
                all_wall_remove = random.sample(potential_no_wall, k=num_remove_wall)
                for key in all_wall_remove:
                    opposite_wall = OPPOSITE[key]
                    
                    dx, dy = MOVES[key]
                    opp_x, opp_y = i+dx, j+dy
                    
                    col[key] = 0
                    grid[opp_x][opp_y][opposite_wall] = 0
        
    return grid

def add_hiding_spot(
    grid: list[list[dict[str, int]]],
    hiding_prob: float,
) -> list[list[dict[str, int]]]:  
    if not grid:
        return None
    
    rows, cols = len(grid), len(grid[0])
    for i, row in enumerate(grid):
        for j, col in enumerate(row):
            no_walls = []
            for move, (dx, dy) in MOVES.items():
                nx, ny = i+dx, j+dy
                if not (0 <= nx <= rows - 1 and 0 <= ny <= cols - 1):
                    continue
                
                opposite_wall = OPPOSITE[move]
                if col[move] == 0 and grid[nx][ny][opposite_wall] == 0:
                    no_walls.append(move)
                
            if len(no_walls) == 1 and random.random() <= hiding_prob:
                col["hiding"] = 1
                
    return grid
    
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
    grid = create(7, 7, wall_prob=0.9)
    print_maze(grid)