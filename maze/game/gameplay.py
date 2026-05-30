import pygame
import sys
import math
from .backbone import *

CELL_SIZE   = 48          
WALL_W      = 3           
WALL_COLOR  = NEON_CYAN
FLOOR_COLOR = (4, 16, 14)
PLAYER_COLOR       = NEON_GREEN
PLAYER_RADIUS      = CELL_SIZE // 4
PLAYER_GLOW_COLOR  = (0, 180, 80)
MOVE_SPEED = 8.0  

def _make_dummy_maze(rows, cols):
    grid = [[{"up": 1, "down": 1, "left": 1, "right": 1}
              for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        col_range = range(cols - 1) if r % 2 == 0 else range(cols - 1, 0, -1)
        for c in col_range:
            if r % 2 == 0:
                grid[r][c]["right"] = 0
                grid[r][c + 1]["left"] = 0
            else:
                grid[r][c]["left"] = 0
                grid[r][c - 1]["right"] = 0
        if r < rows - 1:
            turn_col = cols - 1 if r % 2 == 0 else 0
            grid[r][turn_col]["down"] = 0
            grid[r + 1][turn_col]["up"] = 0
    return grid

class Camera:
    def __init__(self):
        self.offset_x = 0.0
        self.offset_y = 0.0

    def update(self, target_wx, target_wy, lerp=0.12):
        desired_x = SCREEN_WIDTH  / 2 - target_wx
        desired_y = SCREEN_HEIGHT / 2 - target_wy
        self.offset_x += (desired_x - self.offset_x) * lerp
        self.offset_y += (desired_y - self.offset_y) * lerp

    def apply(self, wx, wy):
        return wx + self.offset_x, wy + self.offset_y

class Player:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self._target_wx = float(col * CELL_SIZE + CELL_SIZE // 2)
        self._target_wy = float(row * CELL_SIZE + CELL_SIZE // 2)
        self.wx = self._target_wx
        self.wy = self._target_wy

    def move_to(self, new_row, new_col):
        self.row = new_row
        self.col = new_col
        self._target_wx = float(new_col * CELL_SIZE + CELL_SIZE // 2)
        self._target_wy = float(new_row * CELL_SIZE + CELL_SIZE // 2)

    @property
    def is_moving(self):
        return abs(self.wx - self._target_wx) > 0.5 or \
               abs(self.wy - self._target_wy) > 0.5

    def update(self, dt):
        speed = MOVE_SPEED * CELL_SIZE * dt 
        dx = self._target_wx - self.wx
        dy = self._target_wy - self.wy
        dist = math.hypot(dx, dy)
        if dist <= speed or dist == 0:
            self.wx = self._target_wx
            self.wy = self._target_wy
        else:
            self.wx += dx / dist * speed
            self.wy += dy / dist * speed

    def draw(self, surface, camera, t):
        sx, sy = camera.apply(self.wx, self.wy)
        sx, sy = int(sx), int(sy)
        r = PLAYER_RADIUS
        pulse = 0.5 + 0.5 * math.sin(t * 3.5)
        for ring_r, alpha in [(r + 10, 40), (r + 6, 80), (r + 3, 140)]:
            ring_surf = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
            glow_a = int(alpha * (0.7 + 0.3 * pulse))
            pygame.draw.circle(ring_surf, (*PLAYER_GLOW_COLOR, glow_a),
                               (ring_r + 2, ring_r + 2), ring_r)
            surface.blit(ring_surf, (sx - ring_r - 2, sy - ring_r - 2))
        pygame.draw.circle(surface, PLAYER_COLOR, (sx, sy), r)

def _cell_top_left(row, col):
    return col * CELL_SIZE, row * CELL_SIZE

def draw_maze(surface, maze, camera, rows, cols):
    for r in range(rows):
        for c in range(cols):
            cell = maze[r][c]
            wx, wy = _cell_top_left(r, c)
            sx, sy = camera.apply(wx, wy)
            sx, sy = int(sx), int(sy)
            cs = CELL_SIZE
            floor_rect = pygame.Rect(sx, sy, cs, cs)
            pygame.draw.rect(surface, FLOOR_COLOR, floor_rect)
            if cell.get("up", 0):
                pygame.draw.line(surface, WALL_COLOR, (sx, sy), (sx + cs, sy), WALL_W)
            if cell.get("down", 0):
                pygame.draw.line(surface, WALL_COLOR, (sx, sy + cs), (sx + cs, sy + cs), WALL_W)
            if cell.get("left", 0):
                pygame.draw.line(surface, WALL_COLOR, (sx, sy), (sx, sy + cs), WALL_W)
            if cell.get("right", 0):
                pygame.draw.line(surface, WALL_COLOR, (sx + cs, sy), (sx + cs, sy + cs), WALL_W)

def draw_hud(surface, algo, heuristic, rows, cols, wall_density, t):
    heur_str = f" / {heuristic}" if heuristic else ""
    lines = [
        f"ALGO : {algo}{heur_str}",
        f"GRID : {rows} × {cols}",
        f"WALL : {wall_density:.2f}",
    ]
    hud_x, hud_y = 14, 12
    for i, line in enumerate(lines):
        surf = font_hud.render(line, True, (0, 160, 140))
        surface.blit(surf, (hud_x, hud_y + i * 20))

def draw_minimap(surface, maze, rows, cols, player, goal=None):
    """
    Draw a minimap in the bottom-right corner.
    - Semi-transparent dark panel as background
    - Each cell is a small filled rect; walls drawn as lines on its edges
    - Player shown as a neon green dot at their logical grid cell
    - Goal cell (rows-1, cols-1) shown as a neon pink dot
    """
    MINI_MARGIN  = 12          # gap from screen edge
    MINI_PADDING = 6           # inner padding inside panel
    MINI_MAX     = 160         # max width/height of the map area
 
    # Scale cell size so the whole maze fits in MINI_MAX × MINI_MAX
    cs = max(2, min(MINI_MAX // max(rows, cols), 8))
    map_w = cols * cs
    map_h = rows * cs
 
    panel_w = map_w + MINI_PADDING * 2
    panel_h = map_h + MINI_PADDING * 2
    panel_x = SCREEN_WIDTH  - panel_w - MINI_MARGIN
    panel_y = SCREEN_HEIGHT - panel_h - MINI_MARGIN
 
    # Panel background
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((0, 18, 16, 200))
    pygame.draw.rect(panel, (*NEON_CYAN, 60), panel.get_rect(), 1, border_radius=4)
    surface.blit(panel, (panel_x, panel_y))
 
    # Origin of map content inside panel
    ox = panel_x + MINI_PADDING
    oy = panel_y + MINI_PADDING
 
    MINI_FLOOR = (8, 30, 26)
    MINI_WALL  = NEON_CYAN
    MINI_WALL_A = 160
 
    wall_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
 
    for r in range(rows):
        for c in range(cols):
            cell = maze[r][c]
            cx = ox + c * cs
            cy = oy + r * cs
 
            # Floor
            pygame.draw.rect(surface, MINI_FLOOR, (cx, cy, cs, cs))
 
            # Walls — 1px lines on each active edge
            if cell.get("up", 0):
                pygame.draw.line(wall_surf, (*MINI_WALL, MINI_WALL_A),
                                 (cx, cy), (cx + cs, cy), 1)
            if cell.get("down", 0):
                pygame.draw.line(wall_surf, (*MINI_WALL, MINI_WALL_A),
                                 (cx, cy + cs), (cx + cs, cy + cs), 1)
            if cell.get("left", 0):
                pygame.draw.line(wall_surf, (*MINI_WALL, MINI_WALL_A),
                                 (cx, cy), (cx, cy + cs), 1)
            if cell.get("right", 0):
                pygame.draw.line(wall_surf, (*MINI_WALL, MINI_WALL_A),
                                 (cx + cs, cy), (cx + cs, cy + cs), 1)
 
    surface.blit(wall_surf, (0, 0))
 
    # Goal marker — neon pink square at actual goal position
    if goal is not None:
        g_row, g_col = goal
    else:
        g_row, g_col = rows - 1, cols - 1
    gx = ox + g_col * cs + cs // 2
    gy = oy + g_row * cs + cs // 2
    goal_r = max(1, cs // 3)
    pygame.draw.rect(surface, NEON_PINK,
                     (gx - goal_r, gy - goal_r, goal_r * 2, goal_r * 2))
 
    # Player marker — neon green circle at logical grid position
    px = ox + player.col * cs + cs // 2
    py = oy + player.row * cs + cs // 2
    player_r = max(2, cs // 2)
    pygame.draw.circle(surface, NEON_GREEN, (px, py), player_r)
 
    # "MAP" label above panel
    lbl = font_hud.render("MAP", True, (0, 130, 115))
    surface.blit(lbl, (panel_x + panel_w // 2 - lbl.get_width() // 2,
                        panel_y - lbl.get_height() - 2))

def game_screen(maze, rows, cols, algo, heuristic, wall_density, start_pos, goal_pos, start_t=0.0):
    player  = Player(row=start_pos[0], col=start_pos[0])
    camera  = Camera()
    camera.offset_x = SCREEN_WIDTH  / 2 - player.wx
    camera.offset_y = SCREEN_HEIGHT / 2 - player.wy

    t = start_t
    running = True

    MOVE_DELAY  = 0.18
    MOVE_REPEAT = 0.09
    held_key    = None
    held_timer  = 0.0

    DIR_MAP = {
        pygame.K_UP:    (-1,  0, "up"), pygame.K_w:     (-1,  0, "up"),
        pygame.K_DOWN:  ( 1,  0, "down"), pygame.K_s:     ( 1,  0, "down"),
        pygame.K_LEFT:  ( 0, -1, "left"), pygame.K_a:     ( 0, -1, "left"),
        pygame.K_RIGHT: ( 0,  1, "right"), pygame.K_d:     ( 0,  1, "right"),
    }

    def try_move(dr, dc, wall_key):
        if player.is_moving: return
        nr, nc = player.row + dr, player.col + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            if maze[player.row][player.col].get(wall_key, 1) == 0:
                player.move_to(nr, nc)

    while running:
        dt = clock.tick(FPS) / 1000.0
        t += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key in DIR_MAP:
                    dr, dc, wk = DIR_MAP[event.key]
                    try_move(dr, dc, wk)
                    held_key   = event.key
                    held_timer = 0.0
            elif event.type == pygame.KEYUP:
                if event.key == held_key:
                    held_key = None

        if held_key and held_key in DIR_MAP and not player.is_moving:
            held_timer += dt
            if held_timer >= MOVE_DELAY:
                repeats = int((held_timer - MOVE_DELAY) / MOVE_REPEAT)
                prev    = int((held_timer - MOVE_DELAY - dt) / MOVE_REPEAT)
                if repeats > prev:
                    dr, dc, wk = DIR_MAP[held_key]
                    try_move(dr, dc, wk)

        player.update(dt)
        camera.update(player.wx, player.wy)

        screen.fill((2, 4, 8))
        draw_maze(screen, maze, camera, rows, cols)
        screen.blit(VIGNETTE_SURF, (0, 0))
        player.draw(screen, camera, t)
        draw_hud(screen, algo, heuristic, rows, cols, wall_density, t)
        draw_minimap(screen, maze, rows, cols, player, goal=goal_pos)

        esc_surf = font_hud.render("[ ESC ] menu", True, (0, 100, 90))
        screen.blit(esc_surf, (SCREEN_WIDTH - esc_surf.get_width() - 14, 12))

        pygame.display.flip()

    # Local import prevents circular dependency!
    from .main_menu import main_menu
    main_menu()