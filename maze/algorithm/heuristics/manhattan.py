def compute(
    curr_pos: tuple[int, int], 
    goal: tuple[int, int]
) -> int:
    x1, y1 = curr_pos
    x2, y2 = goal

    return abs(x2 - x1) + abs(y2 - y1)