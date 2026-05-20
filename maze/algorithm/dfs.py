def solve(
    grid: list[list[dict[str, int]]],
    start: tuple[int, int],
    goal: tuple[int, int],
    max_steps: int = 500,
) -> list[tuple[int, int]]: # Code by Copilot AI
    """Solve the maze using recursive depth-first search.

    Each cell in `grid` contains wall flags for `up`, `down`, `left`, and `right`.
    A value of `1` indicates a wall, and `0` indicates an open passage.
    """

    if not grid or not grid[0]:
        return []

    rows = len(grid)
    cols = len(grid[0])
    start_x, start_y = start
    goal_x, goal_y = goal

    if not (0 <= start_x < rows and 0 <= start_y < cols):
        return []
    if not (0 <= goal_x < rows and 0 <= goal_y < cols):
        return []
    if start == goal:
        return [start]
    
    if not max_steps:
        max_steps = float("inf")

    visited: set[tuple[int, int]] = set()
    directions = [
        (-1, 0, "up", "down"),
        (1, 0, "down", "up"),
        (0, -1, "left", "right"),
        (0, 1, "right", "left"),
    ]

    def dfs(x: int, y: int, step: int) -> list[tuple[int, int]] | None:
        if step == max_steps:
            return None

        visited.add((x, y))
        if (x, y) == goal:
            return [(x, y)]

        for dx, dy, wall, opposite_wall in directions:
            next_x = x + dx
            next_y = y + dy

            if not (0 <= next_x < rows and 0 <= next_y < cols):
                continue
            if (next_x, next_y) in visited:
                continue
            if grid[x][y].get(wall, 1) == 1:
                continue
            if grid[next_x][next_y].get(opposite_wall, 1) == 1:
                continue

            result = dfs(next_x, next_y, step + 1)
            if result is not None:
                return [(x, y)] + result

        return None

    path = dfs(start_x, start_y, 0)
    return path if path is not None else []
        