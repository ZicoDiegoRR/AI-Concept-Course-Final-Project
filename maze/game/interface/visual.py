from .backbone import *
import pygame
import math

# ── Tunable layout / style constants ────────────────────────────────────────

CELL_SIZE = 48          # pixels per cell (match MazeRenderer)

WALL_THICKNESS = 4

# Colors (kept consistent with the neon theme used elsewhere in the project)
COLOR_CELL_FLOOR   = (10, 28, 26)
COLOR_WALL         = (0, 255, 220)        # NEON_CYAN
COLOR_HIDING_SPOT  = (180, 0, 255)        # NEON_PURPLE
COLOR_AGENT        = (255, 0, 180)        # NEON_PINK
COLOR_PLAYER       = (0, 255, 120)        # NEON_GREEN
COLOR_FOG          = (2, 4, 8)

COLOR_MINIMAP_BG     = (4, 10, 9)
COLOR_MINIMAP_KNOWN  = (0, 80, 72)
COLOR_MINIMAP_FOG    = (15, 15, 20)
COLOR_MINIMAP_PLAYER = (0, 255, 120)
COLOR_MINIMAP_BORDER = (0, 255, 220)

COLOR_HUD_TEXT     = (200, 255, 248)
COLOR_HUD_WALK     = (0, 255, 120)
COLOR_HUD_SNEAK    = (0, 255, 220)
COLOR_TIMER_NORMAL = (200, 255, 248)
COLOR_TIMER_LOW    = (255, 50, 80)

COLOR_WARNING_SEE  = (255, 50, 80)
COLOR_WARNING_HEAR = (255, 200, 0)

WARNING_DURATION = 5.0  # seconds a warning subtitle stays on screen


class VisualEffects:
    """
    Renders gameplay visuals each frame from a `visual_dict` provided by
    the manager. Maintains small bits of internal timing state (for
    warning subtitle durations) but never mutates the data it receives.

    Expected visual_dict keys:
        player_vision:     list[tuple[int, int]]   - visible cell coords
        player_known_map:  list[list[bool]]        - explored cells for minimap
        agent_see_player:  bool
        agent_hear_player: bool
        remaining_time:    int
        player_walking:    bool

    Additional keys this module looks for opportunistically (if present)
    to render gameplay objects, walls, agent, and player position. If
    absent, those render steps are simply skipped, so this module degrades
    gracefully if the manager hasn't wired everything up yet.

        maze_grid:    list[list[dict]]  - optional, per-cell wall info, e.g.
                                           {"walls": {"N":bool,"S":bool,"E":bool,"W":bool},
                                            "hiding_spot": bool}
        player_pos:   tuple[int, int]
        agent_pos:    tuple[int, int]
        view_origin:  tuple[int, int]   - top-left cell coord of the camera/view
    """

    def __init__(self, view_rect, minimap_rect):
        """
        view_rect:     pygame.Rect, the main gameplay viewport on screen
        minimap_rect:  pygame.Rect, where to draw the minimap
        """
        self.screen = screen
        self.fonts = {
            "hud": font_hud,
            "sub": font_sub,
        }
        self.view_rect = view_rect
        self.minimap_rect = minimap_rect

        # Warning subtitle timers (seconds remaining to display)
        self._see_warning_timer = 0.0
        self._hear_warning_timer = 0.0

        # Minimap caching (performance optimization)
        self._minimap_cache_surface = None
        self._minimap_cache_known = None

    # ── Public API ───────────────────────────────────────────────────────

    def update(self, visual_dict, dt):
        """
        Update internal timers based on the latest visual_dict and elapsed
        time `dt` (seconds). Call once per frame before draw().
        """
        if visual_dict.get("agent_see_player", False):
            self._see_warning_timer = WARNING_DURATION
        elif self._see_warning_timer > 0:
            self._see_warning_timer = max(0.0, self._see_warning_timer - dt)

        if visual_dict.get("agent_hear_player", False):
            self._hear_warning_timer = WARNING_DURATION
        elif self._hear_warning_timer > 0:
            self._hear_warning_timer = max(0.0, self._hear_warning_timer - dt)

    def draw(self, visual_dict):
        """
        Render the full frame according to render priority (low → high so
        higher-priority elements are drawn on top):

            4. Fog Overlay
            3. Minimap
            2. HUD (movement indicator, timer)
            1. Warning Subtitle
        """
        self._draw_fog(
            visual_dict.get("player_vision", []),
            visual_dict.get("view_origin", (0, 0)),
            visual_dict.get("camera_offset", (0.0, 0.0)),
        )
        self._draw_minimap(
            visual_dict.get("maze_grid"),
            visual_dict.get("player_pos"),
            visual_dict.get("player_known_map"),
        )

        self._draw_movement_indicator(visual_dict.get("player_walking", False))
        self._draw_survival_timer(visual_dict.get("remaining_time", 0))

        self._draw_warning_subtitle()

    # ── Field of view rendering ─────────────────────────────────────────

    def _draw_fog(self, player_vision, view_origin, camera_offset):
        """Draw fog only on cells that are not inside the player's vision."""
        fog = pygame.Surface(self.view_rect.size, pygame.SRCALPHA)

        start_row, start_col = view_origin
        offset_x, offset_y = camera_offset
        cols = math.ceil((self.view_rect.width + offset_x) / CELL_SIZE)
        rows = math.ceil((self.view_rect.height + offset_y) / CELL_SIZE)
        vision_set = set(player_vision)

        for row_offset in range(rows):
            for col_offset in range(cols):
                cell = (start_row + row_offset, start_col + col_offset)
                if cell in vision_set:
                    continue
                rect = pygame.Rect(
                    int(col_offset * CELL_SIZE - offset_x),
                    int(row_offset * CELL_SIZE - offset_y),
                    CELL_SIZE,
                    CELL_SIZE,
                )
                fog.fill(COLOR_FOG, rect)

        self.screen.blit(fog, self.view_rect.topleft)

    def _cell_to_screen(self, cell, view_origin):
        """Convert a maze cell coordinate to a top-left screen pixel position."""
        cx, cy = cell
        ox, oy = view_origin
        sx = self.view_rect.x + (cx - ox) * CELL_SIZE
        sy = self.view_rect.y + (cy - oy) * CELL_SIZE
        return sx, sy

    # ── Minimap ──────────────────────────────────────────────────────────

    def _draw_minimap(self, maze_grid, player_pos, known_pos):
        """
        Draw a tiny replica of the maze in the minimap region using cached surface.
        Cache is rebuilt only when known_pos changes.
        """
        rect = self.minimap_rect

        if not maze_grid:
            return

        rows = len(maze_grid)
        cols = len(maze_grid[0]) if rows > 0 else 0

        if rows == 0 or cols == 0:
            return

        # Convert known_pos to tuple for cache comparison
        known_tuple = tuple(tuple(row) for row in known_pos)

        # Rebuild cache if known_pos has changed
        if self._minimap_cache_known != known_tuple:
            self._minimap_cache_surface = self._build_minimap_surface(
                rect, maze_grid, known_pos, rows, cols
            )
            self._minimap_cache_known = known_tuple

        # Draw background and border
        pygame.draw.rect(self.screen, COLOR_MINIMAP_BG, rect)
        pygame.draw.rect(self.screen, COLOR_MINIMAP_BORDER, rect, 2, border_radius=2)

        # Blit cached minimap surface
        if self._minimap_cache_surface:
            self.screen.blit(self._minimap_cache_surface, rect.topleft)

        # Draw player position (fresh each frame)
        if player_pos:
            px, py = player_pos
            if 0 <= px < rows and 0 <= py < cols:
                cell_w = rect.width / cols
                cell_h = rect.height / rows
                center = (
                    int(rect.x + (py + 0.5) * cell_w),
                    int(rect.y + (px + 0.5) * cell_h),
                )
                radius = max(2, int(min(cell_w, cell_h) / 3))
                pygame.draw.circle(self.screen, COLOR_MINIMAP_PLAYER, center, radius)

    def _build_minimap_surface(self, rect, maze_grid, known_pos, rows, cols):
        """
        Build a cached minimap surface showing maze structure and known cells.
        This is called only when known_pos changes.
        """
        # Create surface for minimap content
        minimap_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # Calculate cell size for minimap
        cell_w = rect.width / cols
        cell_h = rect.height / rows
        wall_thickness = max(1, int(min(cell_w, cell_h) / 8))  # thin walls for minimap

        # Draw maze structure and known cells
        for cx in range(rows):
            for cy in range(cols):
                cell_rect = pygame.Rect(
                    cy * cell_w,
                    cx * cell_h,
                    math.ceil(cell_w),
                    math.ceil(cell_h),
                )

                if known_pos[cx][cy]:
                    minimap_surf.fill(COLOR_MINIMAP_KNOWN, cell_rect)

                    # Draw walls for this known cell
                    cell_data = maze_grid[cx][cy]
                    walls = {wall: val for wall, val in cell_data.items() if wall != "hiding"}

                    sx = int(cy * cell_w)
                    sy = int(cx * cell_h)
                    ex = int((cy + 1) * cell_w)
                    ey = int((cx + 1) * cell_h)

                    if walls.get("up"):
                        pygame.draw.line(minimap_surf, COLOR_WALL, (sx, sy), (ex, sy), wall_thickness)
                    if walls.get("down"):
                        pygame.draw.line(minimap_surf, COLOR_WALL, (sx, ey), (ex, ey), wall_thickness)
                    if walls.get("left"):
                        pygame.draw.line(minimap_surf, COLOR_WALL, (sx, sy), (sx, ey), wall_thickness)
                    if walls.get("right"):
                        pygame.draw.line(minimap_surf, COLOR_WALL, (ex, sy), (ex, ey), wall_thickness)
                else:
                    minimap_surf.fill((0, 0, 0), cell_rect)

        return minimap_surf

    # ── HUD: movement indicator & survival timer ────────────────────────

    def _draw_movement_indicator(self, player_walking):
        text = "Movement: Walking" if player_walking else "Movement: Sneaking"
        color = COLOR_HUD_WALK if player_walking else COLOR_HUD_SNEAK
        surf = self.fonts["hud"].render(text, True, color)
        pos = (self.view_rect.x + 10, self.view_rect.bottom - surf.get_height() - 10)
        self.screen.blit(surf, pos)

    def _draw_survival_timer(self, remaining_time):
        color = COLOR_TIMER_LOW if remaining_time <= 10 else COLOR_TIMER_NORMAL
        text = f"Time Remaining: {remaining_time}"
        surf = self.fonts["hud"].render(text, True, color)
        pos = (self.view_rect.x + 10, self.view_rect.y + 10)
        self.screen.blit(surf, pos)

    # ── Warning subtitles ────────────────────────────────────────────────

    def _draw_warning_subtitle(self):
        """
        Draws the highest-priority active warning subtitle, if any.
        "Seen" warning takes precedence over "heard" warning when both
        are active simultaneously.
        """
        text = None
        color = COLOR_HUD_TEXT

        if self._see_warning_timer > 0:
            text = "You feel like someone is watching you."
            color = COLOR_WARNING_SEE
        elif self._hear_warning_timer > 0:
            text = "You feel like your footsteps are too loud."
            color = COLOR_WARNING_HEAR

        if text is None:
            return

        surf = self.fonts["sub"].render(text, True, color)
        pos = surf.get_rect(midbottom=(self.view_rect.centerx, self.view_rect.bottom - 40))
        self.screen.blit(surf, pos)


def make_view_and_minimap_rects(cols, rows, margin=12, max_minimap_px=150,
                                screen_w=None, screen_h=None):
    """
    Compute a `view_rect` and `minimap_rect` for a given maze size.

    - `cols`, `rows`: maze dimensions in cells
    - `margin`: outer margin in pixels
    - `max_minimap_px`: target maximum minimap size in pixels (square area)
    - `screen_w`, `screen_h`: optional screen size override. If omitted,
      attempts to use `SCREEN_WIDTH`/`SCREEN_HEIGHT` (imported from backbone).

    Returns: (view_rect: pygame.Rect, minimap_rect: pygame.Rect)
    """
    if screen_w is None:
        screen_w = globals().get("SCREEN_WIDTH")
    if screen_h is None:
        screen_h = globals().get("SCREEN_HEIGHT")

    if screen_w is None or screen_h is None:
        raise RuntimeError("SCREEN_WIDTH/SCREEN_HEIGHT not found; pass screen_w/screen_h")

    # Pick a minimap cell size that fits the target minimap pixel box.
    max_cell_w = max_minimap_px // max(1, cols)
    max_cell_h = max_minimap_px // max(1, rows)
    cell_px = max(4, min(max_cell_w, max_cell_h))

    minimap_w = cols * cell_px
    minimap_h = rows * cell_px

    # Prevent the minimap from taking more than ~1/3 of the screen width
    minimap_w = min(minimap_w, max(64, screen_w // 3))
    minimap_h = min(minimap_h, screen_h - 2 * margin)

    minimap_rect = pygame.Rect(screen_w - margin - minimap_w, margin, minimap_w, minimap_h)
    view_rect = pygame.Rect(0, 0, screen_w, screen_h)

    return view_rect, minimap_rect


def create_visual_effects(cols, rows, margin=12, max_minimap_px=150):
    """Convenience factory: compute rects from maze size and return a VisualEffects instance."""
    vrect, mrect = make_view_and_minimap_rects(cols, rows, margin, max_minimap_px)
    return VisualEffects(vrect, mrect)