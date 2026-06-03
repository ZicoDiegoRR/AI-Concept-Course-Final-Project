from collections import deque
import random
import copy

def find_disconnected_loc(
    grid: list[list[dict[str, int]]],
    start: tuple[int, int],
    connect_mat: list[list[int]] = None,
) -> list[tuple[int, int]]:
    if not isinstance(grid, list):
        return None
    
    if not all(isinstance(row, list) for row in grid):
        return None

    moves = (
        ((-1, 0), "up", "down"),
        ((1, 0), "down", "up"),
        ((0, -1), "left", "right"),
        ((0, 1), "right", "left")
    )
    
    rows, cols = len(grid), len(grid[0])
    if not connect_mat or (
        len(connect_mat) != len(grid) and len(connect_mat[0]) != len(grid[0])
    ):
        truth_mat = [[0 for _ in range(len(grid[0]))] for _ in range(len(grid))]
    else:
        truth_mat = connect_mat
    
    queue = deque([start])
    visited = set()
    
    while queue:
        curr_pos = queue.popleft()
        
        if curr_pos in visited:
            continue
        
        visited.add(curr_pos)
        curr_x, curr_y = curr_pos
        for (dx, dy), wall, opposite_wall in moves:
            nxt_x, nxt_y = curr_x + dx, curr_y + dy

            if not (0 <= nxt_x < rows and 0 <= nxt_y < cols):
                continue
            if grid[curr_x][curr_y].get(wall, 1) == 1:
                continue
            if grid[nxt_x][nxt_y].get(opposite_wall, 1) == 1:
                continue
            
            truth_mat[nxt_x][nxt_y] = 1
            queue.append((nxt_x, nxt_y))
            
    return truth_mat

def find_next_disconnect(
    mat: list[list[int]],
    visited: list[list[tuple[int, int]]],
    start: tuple[int, int],
) -> list[tuple[int, int]]:
    if not mat or not mat[0]:
        return []
    
    rows = len(mat)
    cols = len(mat[0])

    if not (0 <= start[0] < rows and 0 <= start[1] < cols):
        return []
    
    q = deque([[start, [start]]])
    seen = set()
    moves = (
        ((-1, 0), "up", "down"),
        ((1, 0), "down", "up"),
        ((0, -1), "left", "right"),
        ((0, 1), "right", "left")
    )
    
    while q:
        curr_pos, curr_path = q.popleft()
        
        if curr_pos not in visited:
            return curr_path
        
        if curr_pos in seen:
            continue

        seen.add(curr_pos)
        curr_x, curr_y = curr_pos
        for (dx, dy), wall, opposite_wall in moves:
            nxt_x, nxt_y = curr_x + dx, curr_y + dy

            if not (0 <= nxt_x < rows and 0 <= nxt_y < cols):
                continue
            if (nxt_x, nxt_y) in seen:
                continue
            
            new_path = curr_path + [(nxt_x, nxt_y)]
            q.append([(nxt_x, nxt_y), new_path])
            
    return []

def perform_connection(
    grid: list[list[dict[str, int]]],
) -> list[list[dict[str, int]]]:
    if not isinstance(grid, list) or not all(isinstance(row, list) for row in grid):
        return None
    
    movement_rev = {
        (-1, 0): "up",
        (1, 0): "down",
        (0, -1): "left",
        (0, 1): "right",
    }
    opposite = {
        "up": "down",
        "down": "up",
        "left": "right",
        "right": "left",
    }
    
    rows, cols = len(grid), len(grid[0])
    flood_fill_start = (0, 0)
    connect_mat = find_disconnected_loc(grid=grid, start=flood_fill_start)
    
    while not all(all(True if col == 1 else False for col in row) for row in connect_mat):
        connect_loc = []
        for i in range(rows):
            for j in range(cols):
                if connect_mat[i][j] == 1:
                    connect_loc.append((i, j))
                    
        bfs_start = random.choice(connect_loc)
        next_disconnect_loc = find_next_disconnect(mat=connect_mat, visited=connect_loc, start=bfs_start)
        
        wall_to_carve_cell = next_disconnect_loc[-1]
        x2, y2 = wall_to_carve_cell
        
        wall_to_carve = []
        for (dx, dy), move in movement_rev.items():
            nx, ny = x2+dx, y2+dy
            if not (0 <= nx <= rows - 1 and 0 <= ny <= cols - 1):
                continue
            
            if connect_mat[nx][ny] == 1:
                wall_to_carve.append((nx, ny, move))
                
        (x1, y1, wall) = random.choice(wall_to_carve)
        opposite_wall = opposite[wall]
        
        grid[x1][y1][opposite_wall] = 0
        grid[x2][y2][wall] = 0
        connect_mat = find_disconnected_loc(grid=grid, start=(0, 0), connect_mat=connect_mat)
        
    return grid
            
if __name__ == "__main__":
    grid = [[{'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 0, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 0, 'left': 0, 'right': 0}, {'up': 1, 'down': 0, 'left': 0, 'right': 1}], [{'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 0, 'left': 0, 'right': 0}, {'up': 0, 'down': 0, 'left': 0, 'right': 1}, {'up': 0, 'down': 0, 'left': 1, 'right': 1}], [{'up': 1, 'down': 0, 'left': 1, 'right': 1}, {'up': 1, 'down': 0, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 0, 'left': 0, 'right': 0}, {'up': 0, 'down': 1, 'left': 0, 'right': 0}, {'up': 0, 'down': 0, 'left': 0, 'right': 1}, {'up': 0, 'down': 0, 'left': 1, 'right': 1}], [{'up': 0, 'down': 1, 'left': 1, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 0, 'down': 1, 'left': 0, 'right': 0}, {'up': 1, 'down': 0, 'left': 0, 'right': 0}, {'up': 0, 'down': 1, 'left': 0, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 0}], [{'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 0, 'down': 0, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 0, 'left': 1, 'right': 1}], [{'up': 1, 'down': 0, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 0, 'down': 1, 'left': 0, 'right': 0}, {'up': 1, 'down': 0, 'left': 0, 'right': 1}, {'up': 0, 'down': 0, 'left': 1, 'right': 1}], [{'up': 0, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 1}]]
    mat = find_disconnected_loc(grid=grid, start=(0, 0))
    for row in mat:
        print(row)
        
    new_grid = perform_connection(grid)
        
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
    
    print_maze(new_grid)