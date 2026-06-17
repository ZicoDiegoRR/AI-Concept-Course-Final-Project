"""
maze_implementation.py
----------------------
Renderer module for the Hide & Seek game.
Responsibilities:
  - Render maze, entities, vision, HUD using PyGame
  - Read keyboard input
  - Return player_update dict to Manager each tick
  - Handle Win/Lose screen with local loop

Does NOT contain: pathfinding, AI logic, collision, timer update,
                  win/lose calculation, maze generation, state transition.
"""

import pygame
import math
from .backbone import (
    screen, clock, FPS,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    NEON_CYAN, NEON_PINK, NEON_PURPLE, NEON_GREEN,
    DIM_CYAN, DIM_PINK, DIM_GREEN,
    WHITE, TEXT_COLOR, CELL_SIZE,
    font_title, font_button, font_hud, font_sub,
    draw_neon_text, draw_background, build_blurred_bg,
    SCANLINE_SURF, VIGNETTE_SURF,
    NeonButton,
)

# ── Constants ────────────────────────────────────────────────────────────────

CAMERA_LERP = 0.1     # camera smoothness (0 = no follow, 1 = instant snap)

WALL_COLOR        = NEON_CYAN
WALL_WIDTH        = 2
DOOR_OPEN_COLOR   = NEON_GREEN
DOOR_CLOSED_COLOR = NEON_PURPLE

PLAYER_VISION_COLOR = (0, 255, 220, 40)   # RGBA — bright cyan, semi-transparent
AGENT_VISION_COLOR  = (255, 0, 180, 25)   # RGBA — dim pink, more transparent

GLOW_RADIUS_FACTOR  = 0.55   # glow size relative to cell size
ENTITY_RADIUS_FACTOR = 0.30  # entity circle size relative to cell size


# ── Camera ───────────────────────────────────────────────────────────────────

class Camera:
    """
    Smooth-follow camera centered on the player.
    Converts world (row, col) coordinates to screen (x, y) pixel positions.
    """

    def __init__(self):
        # Camera position in world-pixel space (top-left of viewport)
        self.x = 0.0
        self.y = 0.0

    def update(self, target_row: float, target_col: float):
        """Lerp camera toward the target entity position each frame."""
        target_x = target_col * CELL_SIZE - SCREEN_WIDTH  / 2 + CELL_SIZE / 2
        target_y = target_row * CELL_SIZE - SCREEN_HEIGHT / 2 + CELL_SIZE / 2
        self.x += (target_x - self.x) * CAMERA_LERP
        self.y += (target_y - self.y) * CAMERA_LERP

    def world_to_screen(self, row: float, col: float) -> tuple[float, float]:
        """Convert a world (row, col) position to screen (sx, sy) pixels."""
        sx = col * CELL_SIZE - self.x
        sy = row * CELL_SIZE - self.y
        return sx, sy

    def cell_top_left(self, row: int, col: int) -> tuple[float, float]:
        """Return the top-left pixel corner of a cell on screen."""
        return self.world_to_screen(row, col)

    def cell_center(self, row: float, col: float) -> tuple[float, float]:
        """Return the center pixel of a (possibly fractional) cell position."""
        sx, sy = self.world_to_screen(row, col)
        return sx + CELL_SIZE / 2, sy + CELL_SIZE / 2


# ── MazeRenderer ─────────────────────────────────────────────────────────────

class MazeRenderer:
    """
    Main renderer class. Called once per tick by the Manager.
    """

    def __init__(self):
        self.camera = Camera()
        self._t = 0.0  # elapsed time for animations

        # Interpolation state — player
        self._player_visual_pos: list[float] = [0.0, 0.0]  # [row, col] in world space
        self._player_prev_pos:   tuple[int, int] | None = None
        self._player_moving = False
        self._player_progress = 0.0  # 0.0 → 1.0 interpolation progress

        # Interpolation state — agent
        self._agent_visual_pos: list[float] = [0.0, 0.0]
        self._agent_prev_pos:   tuple[int, int] | None = None
        self._agent_moving = False
        self._agent_progress = 0.0

        self._tick_interval = 0.5

        # Maze wall caching (performance optimization)
        self._maze_cache_surface = None
        self._maze_cache_id = None

    # ── Public API ────────────────────────────────────────────────────────────

    def update(self, game_dict: dict, dt: float) -> dict:
        """
        Main entry point called every tick by Manager.
        Renders everything and returns player_update.
        """
        frame_dt = min(dt, 0.25)
        self._t += frame_dt

        maze         = game_dict["maze"]
        timer        = game_dict["timer"]
        player_pos   = game_dict["player_pos"]
        player_speed = game_dict["player_speed"]
        player_vision= game_dict["player_vision"]
        player_color = game_dict["player_color"]
        agent_pos    = game_dict["agent_pos"]
        agent_speed  = game_dict["agent_speed"]
        agent_vision = game_dict["agent_vision"]
        agent_color  = game_dict["agent_color"]
        
        # ── Win/Lose check ────────────────────────────────────────────────────
        game_status = "running"
        if player_pos == agent_pos:
            game_status = "lose"
        elif timer <= 0:
            game_status = "win"

        # ── Interpolation update ──────────────────────────────────────────────
        interp_step = frame_dt / self._tick_interval if self._tick_interval > 0 else 1.0
        self._player_moving = self._update_interpolation(
            "player", player_pos, player_speed * interp_step
        )
        self._agent_moving = self._update_interpolation(
            "agent", agent_pos, agent_speed * interp_step
        )

        # ── Camera follows visual player position ─────────────────────────────
        self.camera.update(
            self._player_visual_pos[0],
            self._player_visual_pos[1]
        )

        # ── Render pipeline ───────────────────────────────────────────────────
        self._render_background()
        self._render_vision(agent_vision,  AGENT_VISION_COLOR)
        self._render_vision(
            player_vision,
            PLAYER_VISION_COLOR,
        )
        self._render_maze(maze)
        self._render_hiding_spots(maze, player_pos)
        self._render_entities(
            self._player_visual_pos,
            self._agent_visual_pos,
            player_color, agent_color
        )

        # CRT scanline overlay
        screen.blit(SCANLINE_SURF, (0, 0))

        # pygame.display.flip()

        # ── Read input ────────────────────────────────────────────────────────
        if not self._player_moving:
            raw_input = self._read_input()
            move = raw_input["move"]
            toggle_movement = raw_input["pressed_movement_toggle"]
        else:
            move = "none"
            toggle_movement = False
        
        # ── Render win/lose screen (if true) ──────────────────────────────────
        next_state = 3 if game_status == "running" else 0
        if game_status != "running":
            next_state = 0
            show_end_screen(status=game_status)

        view_origin_row = int(self.camera.y / CELL_SIZE)
        view_origin_col = int(self.camera.x / CELL_SIZE)
        camera_offset_x = self.camera.x - view_origin_col * CELL_SIZE
        camera_offset_y = self.camera.y - view_origin_row * CELL_SIZE

        return {
            "move":                    move,
            "pressed_movement_toggle": toggle_movement,
            "state":                   next_state,
            "player_moving":           self._player_moving,
            "agent_moving":            self._agent_moving,
            # Provide camera-origin in cell coordinates for external overlays
            "view_origin": (view_origin_row, view_origin_col),
            "camera_offset": (camera_offset_x, camera_offset_y),
            "player_pos": player_pos,
            "agent_pos": agent_pos,
        }

    # ── Interpolation ─────────────────────────────────────────────────────────

    def _update_interpolation(
        self, entity: str, current_pos: tuple[int, int], speed: float
    ) -> bool:
        """
        Update visual position interpolation for an entity.
        Returns True if the entity is still mid-movement.
        """
        if entity == "player":
            visual   = self._player_visual_pos
            prev     = self._player_prev_pos
            progress = self._player_progress
        else:
            visual   = self._agent_visual_pos
            prev     = self._agent_prev_pos
            progress = self._agent_progress

        cr, cc = current_pos

        # First call — snap to position instantly
        if prev is None:
            visual[0] = float(cr)
            visual[1] = float(cc)
            if entity == "player":
                self._player_prev_pos = current_pos
                self._player_progress = 1.0
            else:
                self._agent_prev_pos = current_pos
                self._agent_progress = 1.0
            return False

        pr, pc = prev

        # New destination detected — start interpolation from scratch
        if (cr, cc) != (pr, pc) and progress >= 1.0:
            progress = 0.0
            if entity == "player":
                self._player_prev_pos = prev  # keep old as start
            else:
                self._agent_prev_pos = prev

        # Advance progress
        if progress < 1.0:
            progress = min(1.0, progress + speed)
            visual[0] = pr + (cr - pr) * progress
            visual[1] = pc + (cc - pc) * progress
        else:
            visual[0] = float(cr)
            visual[1] = float(cc)

        # Persist state
        if entity == "player":
            self._player_progress = progress
            self._player_prev_pos = current_pos if progress >= 1.0 else prev
        else:
            self._agent_progress = progress
            self._agent_prev_pos = current_pos if progress >= 1.0 else prev

        return progress < 1.0

    # ── Render: Background ────────────────────────────────────────────────────

    def _render_background(self):
        """Draw the cyberpunk animated background."""
        draw_background(screen, self._t)

    # ── Render: Vision ────────────────────────────────────────────────────────

    def _render_vision(
        self, vision_cells: list[tuple[int, int]], color: tuple
    ):
        """
        Render a semi-transparent overlay on all visible cells.
        color is an RGBA tuple.
        """
        if not vision_cells:
            return
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for (row, col) in vision_cells:
            sx, sy = self.camera.cell_top_left(row, col)
            rect = pygame.Rect(int(sx), int(sy), CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(overlay, color, rect)
        screen.blit(overlay, (0, 0))

    # ── Render: Maze walls ────────────────────────────────────────────────────

    def _render_maze(self, maze: list):
        """
        Render maze walls by blitting a cached surface.
        Cache is invalidated if maze object reference changes.
        """
        maze_id = id(maze)
        
        # Rebuild cache if maze changed
        if self._maze_cache_id != maze_id:
            self._maze_cache_surface = self._build_maze_surface(maze)
            self._maze_cache_id = maze_id
        
        # Blit cached maze surface, accounting for camera offset
        cam_x = int(self.camera.x)
        cam_y = int(self.camera.y)
        screen.blit(self._maze_cache_surface, (-cam_x, -cam_y))

    def _build_maze_surface(self, maze: list) -> pygame.Surface:
        """
        Build a world-space surface with all maze walls rendered.
        This is called once per unique maze structure, then cached.
        """
        rows = len(maze)
        cols = len(maze[0]) if rows > 0 else 0
        
        # Create world-space surface
        width = cols * CELL_SIZE
        height = rows * CELL_SIZE
        maze_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        for r in range(rows):
            for c in range(cols):
                cell = maze[r][c]
                sx, sy = c * CELL_SIZE, r * CELL_SIZE

                # Top wall
                neighbor_up = maze[r-1][c]["down"] if r > 0 else 1
                if cell["up"] or neighbor_up:
                    self._draw_wall_on_surface(maze_surface, sx, sy, sx + CELL_SIZE, sy)

                # Bottom wall
                neighbor_down = maze[r+1][c]["up"] if r < rows - 1 else 1
                if cell["down"] or neighbor_down:
                    self._draw_wall_on_surface(maze_surface, sx, sy + CELL_SIZE, sx + CELL_SIZE, sy + CELL_SIZE)

                # Left wall
                neighbor_left = maze[r][c-1]["right"] if c > 0 else 1
                if cell["left"] or neighbor_left:
                    self._draw_wall_on_surface(maze_surface, sx, sy, sx, sy + CELL_SIZE)

                # Right wall
                neighbor_right = maze[r][c+1]["left"] if c < cols - 1 else 1
                if cell["right"] or neighbor_right:
                    self._draw_wall_on_surface(maze_surface, sx + CELL_SIZE, sy, sx + CELL_SIZE, sy + CELL_SIZE)
        
        return maze_surface

    def _draw_wall_on_surface(self, surface: pygame.Surface, x1: int, y1: int, x2: int, y2: int):
        """Draw a single neon wall segment on a given surface (for caching)."""
        # Glow layer
        pygame.draw.line(surface, (*WALL_COLOR, 40), (x1, y1), (x2, y2), WALL_WIDTH + 4)
        # Core line
        pygame.draw.line(surface, WALL_COLOR, (x1, y1), (x2, y2), WALL_WIDTH)

    def _draw_wall(self, x1: int, y1: int, x2: int, y2: int):
        """Draw a single neon wall segment with a subtle glow."""
        # Glow layer
        glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(glow_surf, (*WALL_COLOR, 40), (x1, y1), (x2, y2), WALL_WIDTH + 4)
        screen.blit(glow_surf, (0, 0))
        # Core line
        pygame.draw.line(screen, WALL_COLOR, (x1, y1), (x2, y2), WALL_WIDTH)

    # ── Render: Hiding spots ──────────────────────────────────────────────────

    def _render_hiding_spots(self, maze: list, player_pos: tuple[int, int]):
        """
        Render hiding spot cells as doors.
        Door opens when player is directly adjacent outside, closes otherwise.
        """
        rows = len(maze)
        cols = len(maze[0]) if rows > 0 else 0
        pr, pc = player_pos
        player_inside = maze[pr][pc]["hiding"] == 1

        for r in range(rows):
            for c in range(cols):
                cell = maze[r][c]
                if cell["hiding"] != 1:
                    continue

                sx, sy = self.camera.cell_top_left(r, c)
                sx, sy = int(sx), int(sy)

                # Find the open side (no wall = door position)
                door_side = self._find_door_side(cell)
                if door_side is None:
                    continue  # all sides are walled — skip

                # Determine if player is right outside this door
                door_open = False
                if not player_inside:
                    adjacent = {
                        "up":    (r - 1, c),
                        "down":  (r + 1, c),
                        "left":  (r, c - 1),
                        "right": (r, c + 1),
                    }
                    adj_cell = adjacent.get(door_side)
                    if adj_cell and adj_cell == (pr, pc):
                        door_open = True

                self._draw_door(sx, sy, door_side, door_open)

    def _find_door_side(self, cell: dict) -> str | None:
        """Return the first side that has no wall (door goes there)."""
        for side in ("up", "down", "left", "right"):
            if cell[side] == 0:
                return side
        return None

    def _draw_door(self, sx: int, sy: int, side: str, open: bool):
        """Draw door on the given side of a cell."""
        color = DOOR_OPEN_COLOR if open else DOOR_CLOSED_COLOR
        half  = CELL_SIZE // 2
        gap   = CELL_SIZE // 4   # gap in center when door is open

        if side == "up":
            y = sy
            if open:
                pygame.draw.line(screen, color, (sx, y), (sx + half - gap, y), WALL_WIDTH + 1)
                pygame.draw.line(screen, color, (sx + half + gap, y), (sx + CELL_SIZE, y), WALL_WIDTH + 1)
            else:
                pygame.draw.line(screen, color, (sx, y), (sx + CELL_SIZE, y), WALL_WIDTH + 1)

        elif side == "down":
            y = sy + CELL_SIZE
            if open:
                pygame.draw.line(screen, color, (sx, y), (sx + half - gap, y), WALL_WIDTH + 1)
                pygame.draw.line(screen, color, (sx + half + gap, y), (sx + CELL_SIZE, y), WALL_WIDTH + 1)
            else:
                pygame.draw.line(screen, color, (sx, y), (sx + CELL_SIZE, y), WALL_WIDTH + 1)

        elif side == "left":
            x = sx
            if open:
                pygame.draw.line(screen, color, (x, sy), (x, sy + half - gap), WALL_WIDTH + 1)
                pygame.draw.line(screen, color, (x, sy + half + gap), (x, sy + CELL_SIZE), WALL_WIDTH + 1)
            else:
                pygame.draw.line(screen, color, (x, sy), (x, sy + CELL_SIZE), WALL_WIDTH + 1)

        elif side == "right":
            x = sx + CELL_SIZE
            if open:
                pygame.draw.line(screen, color, (x, sy), (x, sy + half - gap), WALL_WIDTH + 1)
                pygame.draw.line(screen, color, (x, sy + half + gap), (x, sy + CELL_SIZE), WALL_WIDTH + 1)
            else:
                pygame.draw.line(screen, color, (x, sy), (x, sy + CELL_SIZE), WALL_WIDTH + 1)

    # ── Render: Entities ──────────────────────────────────────────────────────

    def _render_entities(
        self,
        player_vpos: list[float],
        agent_vpos:  list[float],
        player_color: tuple[int, int, int],
        agent_color:  tuple[int, int, int],
    ):
        """Render player and agent as neon glowing circles."""
        # Draw agent first (behind player)
        self._draw_entity_circle(agent_vpos[0],  agent_vpos[1],  agent_color)
        self._draw_entity_circle(player_vpos[0], player_vpos[1], player_color)

    def _draw_entity_circle(
        self, row: float, col: float, color: tuple[int, int, int]
    ):
        """Draw a single entity as a neon circle with glow."""
        cx, cy = self.camera.cell_center(row, col)
        cx, cy = int(cx), int(cy)
        radius = int(CELL_SIZE * ENTITY_RADIUS_FACTOR)
        glow_r = int(CELL_SIZE * GLOW_RADIUS_FACTOR)

        # # Outer glow
        # glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # pygame.draw.circle(glow_surf, (*color, 35), (cx, cy), glow_r)
        # pygame.draw.circle(glow_surf, (*color, 55), (cx, cy), glow_r // 2)
        # screen.blit(glow_surf, (0, 0))

        # Core circle
        pygame.draw.circle(screen, color, (cx, cy), radius)

        # # Bright center highlight
        # bright = tuple(min(255, int(c * 0.2 + 255 * 0.8)) for c in color)
        # pygame.draw.circle(screen, bright, (cx - radius // 4, cy - radius // 4), radius // 3)

    # ── Render: HUD ───────────────────────────────────────────────────────────

    def _render_hud(self, timer: int):
        """Display timer at top-center of screen."""
        minutes = timer // 60
        seconds = timer % 60
        timer_str = f"{minutes:02d}:{seconds:02d}"
        draw_neon_text(
            screen, timer_str, font_hud, NEON_CYAN,
            (SCREEN_WIDTH // 2, 24), glow_alpha=80
        )

    # ── Input ─────────────────────────────────────────────────────────────────

    def _read_input(self) -> dict:
        """
        Read keyboard events and return raw input dict.
        Processes one movement key per tick (priority: W/A/S/D).
        """
        move = "none"
        pressed_toggle = False
        state = 3  # default: gameplay running

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = 0  # back to main menu

                if event.key == pygame.K_c:
                    pressed_toggle = True

                # Movement keys
                if event.key in (pygame.K_w, pygame.K_UP):
                    move = "up"
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    move = "down"
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    move = "left"
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    move = "right"

        return {
            "move": move,
            "pressed_movement_toggle": pressed_toggle,
            "state": state,
        }


# ── Win / Lose Screen (local loop) ───────────────────────────────────────────

def show_end_screen(status: str) -> int:
    """
    Display win or lose screen with a local pygame loop.
    Returns 0 when the player clicks "Back" to return to main menu.

    Parameters
    ----------
    status : str
        "win" or "lose"
    """
    t = 0.0
    bg = build_blurred_bg(t)

    if status == "win":
        title_text  = "YOU WIN"
        title_color = NEON_GREEN
    else:
        title_text  = "CAUGHT"
        title_color = NEON_PINK

    back_btn = NeonButton(
        SCREEN_WIDTH // 2,
        SCREEN_HEIGHT // 2 + 100,
        "[ BACK ]",
        color_main=NEON_CYAN,
        color_dim=DIM_CYAN,
    )

    while True:
        dt = clock.tick(FPS) / 1000.0
        t += dt
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_btn.is_clicked(mouse_pos):
                    return 0

        # Background
        screen.blit(bg, (0, 0))
        screen.blit(VIGNETTE_SURF, (0, 0))

        # Pulsing title
        pulse = 0.5 + 0.5 * math.sin(t * 3.0)
        glow  = int(60 + pulse * 80)
        draw_neon_text(
            screen, title_text, font_title, title_color,
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60),
            glow_alpha=glow
        )

        # Subtitle
        sub_text = "You survived!" if status == "win" else "The seeker found you."
        draw_neon_text(
            screen, sub_text, font_sub, TEXT_COLOR,
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10),
            glow_alpha=40
        )

        # Back button
        back_btn.update(mouse_pos, dt)
        back_btn.draw(screen)

        # CRT effect
        screen.blit(SCANLINE_SURF, (0, 0))

        pygame.display.flip()
