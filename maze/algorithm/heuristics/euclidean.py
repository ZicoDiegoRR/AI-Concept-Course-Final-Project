def compute(
    curr_pos: tuple[int, int], 
    goal: tuple[int, int]
) -> int:
    x1, y1 = curr_pos
    x2, y2 = goal

    return ((x2 - x1)**2 + (y2 - y1)**2)**0.5