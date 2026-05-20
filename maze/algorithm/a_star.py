import heapq

def solve(
    grid: list[list[dict[str, int]]],
    start: tuple[int, int],
    goal: tuple[int, int],
    h_func: function,
    max_steps: int = 500,
) -> list[tuple[int, int]]:
    if not grid or not grid[0]:
        return []
    
    rows = len(grid)
    cols = len(grid[0])

    if not (0 <= start[0] < rows and 0 <= start[1] < cols):
        return []
    if not (0 <= goal[0] < rows and 0 <= goal[1] < cols):
        return []
    if start == goal:
        return [start]
    
    if not max_steps:
        max_steps = float("inf")
    
    q = [[0, 0, 0, start, [start]]]
    visited = set()
    moves = (
        ((-1, 0), "up", "down"),
        ((1, 0), "down", "up"),
        ((0, -1), "left", "right"),
        ((0, 1), "right", "left")
    )
    
    while q:
        _, curr_g, curr_step, curr_pos, curr_path = heapq.heappop(q)
        
        if curr_pos == goal:
            return curr_path
        
        if curr_pos in visited or curr_step >= max_steps:
            continue
        
        visited.add(curr_pos)
        curr_x, curr_y = curr_pos
        for (dx, dy), wall, opposite_wall in moves:
            nxt_x, nxt_y = curr_x + dx, curr_y + dy

            if not (0 <= nxt_x < rows and 0 <= nxt_y < cols):
                continue
            if (nxt_x, nxt_y) in visited:
                continue
            if grid[curr_x][curr_y].get(wall, 1) == 1:
                continue
            if grid[nxt_x][nxt_y].get(opposite_wall, 1) == 1:
                continue
            
            new_path = curr_path + [(nxt_x, nxt_y)]
            new_g = curr_g + 1
            new_f = new_g + h_func(curr_pos, goal)
            
            heapq.heappush(q, [new_f, new_g, curr_step+1, (nxt_x, nxt_y), new_path])
            
    return []

if __name__ == "__main__":
    import heuristics.euclidean as euclidean
    
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
    goal = (3, 6)
    print(solve(grid, start, goal, euclidean.compute))