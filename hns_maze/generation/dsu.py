# Code by Claude AI

import random

class DisjointSet:
    """Union-Find with path compression and union by rank."""
    
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        # Path compression: point directly to root
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root
    
    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False  # already connected
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


def perform_connection(
    grid: list[list[dict[str, int]]],
) -> list[list[dict[str, int]]]:
    if not isinstance(grid, list) or not all(isinstance(row, list) for row in grid):
        return None

    rows, cols = len(grid), len(grid[0])
    if rows == 0 or cols == 0:
        return grid

    opposite = {"up": "down", "down": "up", "left": "right", "right": "left"}

    def idx(r, c):
        return r * cols + c

    dsu = DisjointSet(rows * cols)

    # --- Pass 1: union every pair of cells that are already connected (no wall) ---
    # Also collect every "wall edge" (adjacent cells, but blocked) as a candidate
    # for carving later.
    wall_edges = []  # (r1, c1, wall_name, r2, c2)

    for r in range(rows):
        for c in range(cols):
            # Only check "down" and "right" per cell to visit each edge once
            for (dx, dy), wall in (((1, 0), "down"), ((0, 1), "right")):
                nr, nc = r + dx, c + dy
                if not (0 <= nr < rows and 0 <= nc < cols):
                    continue

                opp = opposite[wall]
                is_open = grid[r][c].get(wall, 1) == 0 and grid[nr][nc].get(opp, 1) == 0

                if is_open:
                    dsu.union(idx(r, c), idx(nr, nc))
                else:
                    wall_edges.append((r, c, wall, nr, nc))

    # --- Pass 2: carve walls between different regions until everything is one region ---
    # Shuffle so the maze doesn't always get connected in the same pattern.
    random.shuffle(wall_edges)

    num_regions = rows * cols
    # num_regions currently counts singleton-find roots; compute actual count:
    roots = {dsu.find(idx(r, c)) for r in range(rows) for c in range(cols)}
    num_regions = len(roots)

    for (r1, c1, wall, r2, c2) in wall_edges:
        if num_regions == 1:
            break

        root1, root2 = dsu.find(idx(r1, c1)), dsu.find(idx(r2, c2))
        if root1 == root2:
            continue  # already same region, carving here wouldn't help

        # Carve the wall
        opp = opposite[wall]
        grid[r1][c1][wall] = 0
        grid[r2][c2][opp] = 0

        dsu.union(idx(r1, c1), idx(r2, c2))
        num_regions -= 1

    return grid