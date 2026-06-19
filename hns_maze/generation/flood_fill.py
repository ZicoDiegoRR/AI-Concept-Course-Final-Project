from collections import deque
import random

def find_disconnected_loc(
    grid: list[list[dict[str, int]]],
    start: tuple[int, int],
    connect_mat: list[list[int]] = None,
) -> list[tuple[int, int]]:
    if not isinstance(grid, list):
        return None
    
    if not all(isinstance(row, list) for row in grid):
        return None

    move_collection = (
        ((-1, 0), "up", "down"),
        ((1, 0), "down", "up"),
        ((0, -1), "left", "right"),
        ((0, 1), "right", "left")
    )
    move_dict = {
        "up": (-1, 0),
        "down": (1, 0),
        "left": (0, -1),
        "right": (0, 1),
    }
    opposite_dict = {
        "up": "down",
        "down": "up",
        "left": "right",
        "right": "left",
    }
    
    rows, cols = len(grid), len(grid[0])
    if not connect_mat or (
        len(connect_mat) != len(grid) or len(connect_mat[0]) != len(grid[0])
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
        for (dx, dy), wall, opposite_wall in move_collection:
            nxt_x, nxt_y = curr_x + dx, curr_y + dy

            if not (0 <= nxt_x < rows and 0 <= nxt_y < cols):
                continue
            if (
                grid[curr_x][curr_y].get(wall, 1) == 1
                or grid[nxt_x][nxt_y].get(opposite_wall, 1) == 1
            ):
                continue
            
            truth_mat[nxt_x][nxt_y] = 1
            queue.append((nxt_x, nxt_y))
            
    return truth_mat

def find_next_disconnect(mat, visited_set, start):
    """Find a cell on the boundary of the unreached region, adjacent to `visited_set`."""
    rows, cols = len(mat), len(mat[0])
    q = deque([start])
    seen = {start}
    moves = ((-1, 0), (1, 0), (0, -1), (0, 1))

    while q:
        x, y = q.popleft()
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < rows and 0 <= ny < cols):
                continue
            if (nx, ny) in seen:
                continue
            if (nx, ny) not in visited_set:
                return (nx, ny)   # found the boundary cell directly
            seen.add((nx, ny))
            q.append((nx, ny))

    return None

def perform_connection(grid):
    if not isinstance(grid, list) or not all(isinstance(row, list) for row in grid):
        return None

    opposite = {"up": "down", "down": "up", "left": "right", "right": "left"}
    movement_rev = {(-1, 0): "up", (1, 0): "down", (0, -1): "left", (0, 1): "right"}

    rows, cols = len(grid), len(grid[0])
    connect_mat = find_disconnected_loc(grid=grid, start=(0, 0))

    connect_loc = {(i, j) for i in range(rows) for j in range(cols) if connect_mat[i][j] == 1}

    while len(connect_loc) < rows * cols:
        bfs_start = random.choice(tuple(connect_loc))
        disconnect_cell = find_next_disconnect(connect_mat, connect_loc, bfs_start)
        if disconnect_cell is None:
            break  # shouldn't happen, but avoid infinite loop

        x2, y2 = disconnect_cell
        wall_to_carve = []
        for (dx, dy), move in movement_rev.items():
            nx, ny = x2 + dx, y2 + dy
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) in connect_loc:
                wall_to_carve.append((nx, ny, move))

        x1, y1, wall = random.choice(wall_to_carve)
        opp = opposite[wall]
        grid[x1][y1][opp] = 0
        grid[x2][y2][wall] = 0

        # incrementally flood-fill just the newly attached region
        newly_reachable = find_disconnected_loc(grid=grid, start=disconnect_cell)
        for i in range(rows):
            for j in range(cols):
                if newly_reachable[i][j] == 1:
                    connect_mat[i][j] = 1
                    connect_loc.add((i, j))

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