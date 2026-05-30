import copy
import random

# Code correction by Claude AI
def add(
    grid: list[list[dict[str, int]]],
    start: tuple[int, int] = None,
    goal: tuple[int, int] = None,
) -> tuple[tuple[int, int], tuple[int, int], list[tuple[int, int]]]:
    rows = len(grid)
    cols = len(grid[0])

    # ── Bug fix 1: randint(1, rows-2) crashes when rows <= 2 ─────────────────
    # Clamp the interior range so it never produces an empty randrange.
    # For a 1- or 2-row grid the only safe interior row is 0 (or the only row),
    # so we fall back to clamping both ends to valid indices.
    if not start:
        r_lo = min(1, rows - 1)
        r_hi = max(r_lo, rows - 2)
        c_lo = min(1, cols - 1)
        c_hi = max(c_lo, cols - 2)
        start = (random.randint(r_lo, r_hi), random.randint(c_lo, c_hi))

    if not goal:
        goal_x = random.randint(0, rows - 1)
        if goal_x == 0 or goal_x == rows - 1:
            goal_y = random.randint(0, cols - 1)
        else:
            goal_y = random.choice([0, cols - 1])
        goal = (goal_x, goal_y)

    # Make sure start != goal
    while goal == start:
        goal_x = random.randint(0, rows - 1)
        if goal_x == 0 or goal_x == rows - 1:
            goal_y = random.randint(0, cols - 1)
        else:
            goal_y = random.choice([0, cols - 1])
        goal = (goal_x, goal_y)

    # Randomised DFS: stack holds (cell, path_so_far)
    # Walks freely through grid coordinates (wall-agnostic); apply_to_grid
    # will carve the walls open along whatever path is found.
    q = [[goal, [goal]]]
    visited = set()
    step = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while q:
        (cx, cy), path = q.pop()

        if (cx, cy) == start:
            return start, goal, path

        if (cx, cy) in visited:
            continue
        visited.add((cx, cy))

        neighbours = random.sample(step, k=4)
        new_nodes = []
        for (dx, dy) in neighbours:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < rows and 0 <= ny < cols and (nx, ny) not in visited:
                new_nodes.append([(nx, ny), path + [(nx, ny)]])

        # Shuffle so the DFS explores in a random order
        random.shuffle(new_nodes)
        q.extend(new_nodes)

    # Should never happen on a fully connected finite grid, but return
    # a sentinel rather than crashing callers.
    return start, goal, None


def apply_to_grid_from_goal(
    grid: list[list[dict[str, int]]],
    path: list[tuple[int, int]],
) -> list[list[dict[str, int]]] | None:
    # ── Bug fix 2: path is None when add() found no route ────────────────────
    if path is None:
        return None

    rows = len(grid)
    cols = len(grid[0])

    opposite = {
        "up": "down", "down": "up",
        "left": "right", "right": "left",
    }
    moves = {
        (-1, 0): "up",
        (1,  0): "down",
        (0, -1): "left",
        (0,  1): "right",
    }

    # ── Bug fix 3: open ALL border walls for corner/edge goal cells ───────────
    # The goal sits on the grid boundary. Open every outward-facing border wall
    # it has so the player can actually exit (or enter from) outside.
    goal_x, goal_y = path[0]
    if goal_x == 0:
        grid[goal_x][goal_y]["up"] = 0
    if goal_x == rows - 1:
        grid[goal_x][goal_y]["down"] = 0
    if goal_y == 0:
        grid[goal_x][goal_y]["left"] = 0
    if goal_y == cols - 1:
        grid[goal_x][goal_y]["right"] = 0

    # ── Bug fix 4: handle single-element path (start == goal) ────────────────
    if len(path) == 1:
        # Nothing to carve; goal border already opened above.
        return grid

    # Carve walls along the path (goal → start direction).
    # Each step opens both sides of the shared wall between consecutive cells.
    curr = path[0]
    for (x, y) in path[1:]:
        curr_x, curr_y = curr
        dx, dy = x - curr_x, y - curr_y
        movement      = moves[(dx, dy)]
        opposite_move = opposite[movement]

        grid[curr_x][curr_y][movement]  = 0
        grid[x][y][opposite_move]       = 0

        curr = (x, y)

    return grid


# ── Smoke test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    def print_maze(grid):
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

    def verify_path_open(grid, path):
        """Walk path and confirm every consecutive wall pair is open."""
        moves = {(-1,0):"up",(1,0):"down",(0,-1):"left",(0,1):"right"}
        opposite = {"up":"down","down":"up","left":"right","right":"left"}
        for i in range(len(path) - 1):
            r1, c1 = path[i]
            r2, c2 = path[i + 1]
            d = moves[(r2-r1, c2-c1)]
            if grid[r1][c1][d] != 0:
                return False, (r1,c1), d
            if grid[r2][c2][opposite[d]] != 0:
                return False, (r2,c2), opposite[d]
        return True, None, None

    sample_grid = [
        [{'up':1,'down':1,'left':1,'right':0},{'up':1,'down':1,'left':0,'right':1},{'up':1,'down':1,'left':1,'right':1},{'up':1,'down':0,'left':1,'right':1},{'up':1,'down':1,'left':1,'right':0},{'up':1,'down':1,'left':0,'right':1},{'up':1,'down':1,'left':1,'right':1}],
        [{'up':1,'down':1,'left':1,'right':0},{'up':1,'down':1,'left':0,'right':1},{'up':1,'down':1,'left':1,'right':1},{'up':0,'down':1,'left':1,'right':0},{'up':1,'down':0,'left':0,'right':0},{'up':1,'down':1,'left':0,'right':1},{'up':1,'down':1,'left':1,'right':1}],
        [{'up':1,'down':0,'left':1,'right':1},{'up':1,'down':0,'left':1,'right':1},{'up':1,'down':1,'left':1,'right':0},{'up':1,'down':1,'left':0,'right':1},{'up':0,'down':1,'left':1,'right':1},{'up':1,'down':0,'left':1,'right':1},{'up':1,'down':0,'left':1,'right':1}],
        [{'up':0,'down':1,'left':1,'right':1},{'up':0,'down':1,'left':1,'right':1},{'up':1,'down':1,'left':1,'right':0},{'up':1,'down':1,'left':0,'right':1},{'up':1,'down':1,'left':1,'right':0},{'up':0,'down':1,'left':0,'right':1},{'up':0,'down':1,'left':1,'right':1}],
        [{'up':1,'down':1,'left':1,'right':0},{'up':1,'down':1,'left':0,'right':0},{'up':1,'down':1,'left':0,'right':1},{'up':1,'down':1,'left':1,'right':1},{'up':1,'down':0,'left':1,'right':0},{'up':1,'down':1,'left':0,'right':1},{'up':1,'down':0,'left':1,'right':1}],
        [{'up':1,'down':0,'left':1,'right':1},{'up':1,'down':1,'left':1,'right':1},{'up':1,'down':1,'left':1,'right':1},{'up':1,'down':1,'left':1,'right':0},{'up':0,'down':1,'left':0,'right':0},{'up':1,'down':0,'left':0,'right':1},{'up':0,'down':0,'left':1,'right':1}],
        [{'up':0,'down':1,'left':1,'right':1},{'up':1,'down':1,'left':1,'right':1},{'up':1,'down':1,'left':1,'right':0},{'up':1,'down':1,'left':0,'right':1},{'up':1,'down':1,'left':1,'right':1},{'up':0,'down':1,'left':1,'right':1},{'up':0,'down':1,'left':1,'right':1}],
    ]

    print("=== Original maze ===")
    print_maze(sample_grid)

    grid_copy = copy.deepcopy(sample_grid)
    start, goal, path = add(grid_copy)
    print(f"\nstart={start}  goal={goal}")
    print(f"path length={len(path) if path else 'None'}")

    result = apply_to_grid_from_goal(grid_copy, path)
    print("\n=== Maze with solution carved ===")
    print_maze(result)

    ok, bad_cell, bad_dir = verify_path_open(result, path)
    print(f"\nPath fully open: {ok}")
    if not ok:
        print(f"  Blocked at cell {bad_cell} direction '{bad_dir}'")

    # Edge-case tests
    print("\n--- Edge case: 2×2 grid ---")
    g2 = [[{'up':1,'down':1,'left':1,'right':1} for _ in range(2)] for _ in range(2)]
    s2, g2_goal, p2 = add(copy.deepcopy(g2))
    print(f"start={s2} goal={g2_goal} path={p2}")

    print("\n--- Edge case: 1×5 grid ---")
    g1 = [[{'up':1,'down':1,'left':1,'right':1} for _ in range(5)]]
    s1, g1_goal, p1 = add(copy.deepcopy(g1))
    print(f"start={s1} goal={g1_goal} path={p1}")

    print("\n--- Edge case: None path passed to apply ---")
    result_none = apply_to_grid_from_goal(copy.deepcopy(sample_grid), None)
    print(f"Result: {result_none}")

    print("\n--- Stress test: 100 random runs, verify path always open ---")
    failures = 0
    for _ in range(100):
        g = copy.deepcopy(sample_grid)
        s, go, p = add(g)
        r = apply_to_grid_from_goal(g, p)
        if r is None or p is None:
            failures += 1
            continue
        ok, _, _ = verify_path_open(r, p)
        if not ok:
            failures += 1
    print(f"Failures: {failures}/100")