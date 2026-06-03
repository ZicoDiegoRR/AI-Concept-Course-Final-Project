from collections import deque

def solve(
    grid: list[list[dict[str, int]]],
    visited: list[list[tuple[int, int]]],
    start: tuple[int, int],
) -> list[tuple[int, int]]:
    if not grid or not grid[0]:
        return []
    
    rows = len(grid)
    cols = len(grid[0])

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
            if grid[curr_x][curr_y].get(wall, 1) == 1:
                continue
            if grid[nxt_x][nxt_y].get(opposite_wall, 1) == 1:
                continue
            
            new_path = curr_path + [(nxt_x, nxt_y)]
            q.append([(nxt_x, nxt_y), new_path])
            
    return []

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
    
    grid = [[{'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 0, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 0, 'left': 0, 'right': 0}, {'up': 1, 'down': 0, 'left': 0, 'right': 1}], [{'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 0, 'left': 0, 'right': 0}, {'up': 0, 'down': 0, 'left': 0, 'right': 1}, {'up': 0, 'down': 0, 'left': 1, 'right': 1}], [{'up': 1, 'down': 0, 'left': 1, 'right': 1}, {'up': 1, 'down': 0, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 0, 'left': 0, 'right': 0}, {'up': 0, 'down': 1, 'left': 0, 'right': 0}, {'up': 0, 'down': 0, 'left': 0, 'right': 1}, {'up': 0, 'down': 0, 'left': 1, 'right': 1}], [{'up': 0, 'down': 1, 'left': 1, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 0, 'down': 1, 'left': 0, 'right': 0}, {'up': 1, 'down': 0, 'left': 0, 'right': 0}, {'up': 0, 'down': 1, 'left': 0, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 0}], [{'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 0, 'down': 0, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 0, 'left': 1, 'right': 1}], [{'up': 1, 'down': 0, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 0, 'down': 1, 'left': 0, 'right': 0}, {'up': 1, 'down': 0, 'left': 0, 'right': 1}, {'up': 0, 'down': 0, 'left': 1, 'right': 1}], [{'up': 0, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 0}, {'up': 1, 'down': 1, 'left': 0, 'right': 1}, {'up': 1, 'down': 1, 'left': 1, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 1}, {'up': 0, 'down': 1, 'left': 1, 'right': 1}]]
    print_maze(grid)  
    print()
    
    start = (4, 4)
    visited = [(4, 4), (3, 4), (5, 4), (4, 5), (3, 3), (3, 5), (5, 3), (5, 5)]
    print(solve(grid, visited, start))