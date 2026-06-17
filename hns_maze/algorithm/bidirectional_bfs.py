from collections import deque

def solve(
    grid: list[list[dict[str, int]]],
    start: tuple[int, int],
    goal: tuple[int, int],
    max_steps: int = 500,
) -> list[tuple[int, int]]: # Code modified from GeeksforGeeks and corrected by Copilot AI
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
        
    queue_start = deque([[start, 0]])
    queue_goal = deque([[goal, 0]])
    visited_start = set()
    visited_goal = set()
    parent_start = {start: None}
    parent_goal = {goal: None}
    
    moves = (
        ((-1, 0), "up", "down"),
        ((1, 0), "down", "up"),
        ((0, -1), "left", "right"),
        ((0, 1), "right", "left")
    )
    
    while queue_start and queue_goal:
        for q, visited, parent in zip(
            [queue_start, queue_goal], 
            [visited_start, visited_goal],
            [parent_start, parent_goal],
        ):
            curr_pos, curr_step = q.popleft()
        
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
                
                q.append([(nxt_x, nxt_y), curr_step + 1])
                parent[(nxt_x, nxt_y)] = curr_pos
                
        intersect = None
        for node in visited_start:
            if node in visited_goal:
                intersect = node
                break

        if intersect is not None:
            path = []
            step = intersect
            while step is not None:
                path.append(step)
                step = parent_start.get(step)
            path.reverse()
            
            step = parent_goal[intersect]
            while step is not None:
                path.append(step)
                step = parent_goal.get(step)
                
            return path
        
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
    goal = (3, 6)
    print(solve(grid, start, goal))