import random

def create(
    rows: int,
    cols: int,
    wall_prob: float = 0.5,
) -> list[list[dict[str, int]]]:
    grid = [[{"up": 0, "down": 0, "left": 0,"right": 0} for _ in range(cols)] for _ in range(rows)]
    opposite = {
        "up": "down", "down": "up",
        "left": "right", "right": "left"
    }
    moves = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1)
    }

    for i, row  in enumerate(grid):
        for j, col in enumerate(row):
            if i == 0: col["up"] = 1
            elif i == len(grid) - 1: col["down"] = 1
            
            if j == 0: col["left"] = 1
            elif j == len(grid[0]) - 1: col["right"] = 1
            
            no_walls = [key for key, val in col.items() if val == 0]
            print(len(no_walls))
            if len(no_walls) >= 2:
                num_add_walls = random.randint(1, len(no_walls) - 1)
                select_walls = random.sample(no_walls, k=num_add_walls)
                
                for wall in select_walls:
                    if random.random() <= wall_prob:
                        col[wall] = 1
                        
                        dx, dy = moves[wall]
                        adj_wall = opposite[wall]
                        
                        adj_x, adj_y = i+dx, j+dy
                        grid[adj_x][adj_y][adj_wall] = 1
        
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