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

# Fullscreen map constants
FULLSCREEN_MAP_KEY    = pygame.K_m
FULLSCREEN_MAP_MARGIN = 40  
COLOR_FULLSCREEN_BG   = (2, 6, 5)
FULLSCREEN_CELL_PX    = 24  # Default cell size


class VisualEffects:
    def __init__(self, view_rect, minimap_rect):
        self.screen = screen
        self.fonts = {
            "hud": font_hud,
            "sub": font_sub,
        }
        self.view_rect = view_rect
        self.minimap_rect = minimap_rect

        # Warning subtitle timers
        self._see_warning_timer = 0.0
        self._hear_warning_timer = 0.0

        # Minimap caching
        self._minimap_cache_surface = None
        self._minimap_cache_known = None

        # Fullscreen map state
        self._fullscreen_cache_surface = None
        self._fullscreen_cache_known = None
        self._fullscreen_cache_size = None
        self._fullscreen_cache_cell_px = None  # Tracks cell size for cache invalidation
        
        self._map_cell_px = FULLSCREEN_CELL_PX # Current zoom level

        # Fullscreen map camera state
        self._map_cam_x = 0.0
        self._map_cam_y = 0.0
        self._map_dragging = False
        self._map_drag_last_mouse = (0, 0)

    def update(self, visual_dict, dt):
        if visual_dict.get("agent_see_player", False):
            self._see_warning_timer = WARNING_DURATION
        elif self._see_warning_timer > 0:
            self._see_warning_timer = max(0.0, self._see_warning_timer - dt)

        if visual_dict.get("agent_hear_player", False):
            self._hear_warning_timer = WARNING_DURATION
        elif self._hear_warning_timer > 0:
            self._hear_warning_timer = max(0.0, self._hear_warning_timer - dt)

    def draw(self, visual_dict):
        if visual_dict.get("map_pressed"):
            self._draw_fullscreen_map(
                visual_dict.get("maze_grid"),
                visual_dict.get("player_pos"),
                visual_dict.get("player_known_map"),
            )
            return

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
        self._draw_fps_counter(visual_dict["fps"])
        self._draw_map_tip()
        self._draw_survival_timer(visual_dict.get("remaining_time", 0))
        self._draw_warning_subtitle()

    # ── Field of view rendering ─────────────────────────────────────────

    def _draw_fog(self, player_vision, view_origin, camera_offset):
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
        cx, cy = cell
        ox, oy = view_origin
        sx = self.view_rect.x + (cx - ox) * CELL_SIZE
        sy = self.view_rect.y + (cy - oy) * CELL_SIZE
        return sx, sy

    # ── Minimap ──────────────────────────────────────────────────────────

    def _draw_minimap(self, maze_grid, player_pos, known_pos):
        rect = self.minimap_rect

        if not maze_grid:
            return

        rows = len(maze_grid)
        cols = len(maze_grid[0]) if rows > 0 else 0

        if rows == 0 or cols == 0:
            return

        known_tuple = tuple(tuple(row) for row in known_pos)

        if self._minimap_cache_known != known_tuple:
            self._minimap_cache_surface = self._build_minimap_surface(
                rect, maze_grid, known_pos, rows, cols
            )
            self._minimap_cache_known = known_tuple

        pygame.draw.rect(self.screen, COLOR_MINIMAP_BG, rect)
        pygame.draw.rect(self.screen, COLOR_MINIMAP_BORDER, rect, 2, border_radius=2)

        if self._minimap_cache_surface:
            self.screen.blit(self._minimap_cache_surface, rect.topleft)

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
        minimap_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        cell_w = rect.width / cols
        cell_h = rect.height / rows
        wall_thickness = max(1, int(min(cell_w, cell_h) / 8))

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

    # ── Fullscreen map overlay ───────────────────────────────────────────

    def _build_fullscreen_surface(self, maze_grid, known_pos, rows, cols, cell_px):
        surf = pygame.Surface((cols * cell_px, rows * cell_px), pygame.SRCALPHA)
        wall_thickness = max(1, int(cell_px / 8))

        for cx in range(rows):
            for cy in range(cols):
                cell_rect = pygame.Rect(cy * cell_px, cx * cell_px, cell_px, cell_px)

                if known_pos[cx][cy]:
                    surf.fill(COLOR_MINIMAP_KNOWN, cell_rect)
                    cell_data = maze_grid[cx][cy]
                    walls = {wall: val for wall, val in cell_data.items() if wall != "hiding"}

                    sx = cy * cell_px
                    sy = cx * cell_px
                    ex = (cy + 1) * cell_px
                    ey = (cx + 1) * cell_px

                    if walls.get("up"):
                        pygame.draw.line(surf, COLOR_WALL, (sx, sy), (ex, sy), wall_thickness)
                    if walls.get("down"):
                        pygame.draw.line(surf, COLOR_WALL, (sx, ey), (ex, ey), wall_thickness)
                    if walls.get("left"):
                        pygame.draw.line(surf, COLOR_WALL, (sx, sy), (sx, ey), wall_thickness)
                    if walls.get("right"):
                        pygame.draw.line(surf, COLOR_WALL, (ex, sy), (ex, ey), wall_thickness)
                else:
                    surf.fill((0, 0, 0), cell_rect)

        return surf

    def _update_fullscreen_cache(self, maze_grid, known_pos, rows, cols):
        """Helper to rebuild the map surface if data or zoom level has changed."""
        known_tuple = tuple(tuple(row) for row in known_pos)
        size_key = (rows, cols)

        if (self._fullscreen_cache_known != known_tuple
                or self._fullscreen_cache_size != size_key
                or self._fullscreen_cache_cell_px != self._map_cell_px
                or self._fullscreen_cache_surface is None):
            self._fullscreen_cache_surface = self._build_fullscreen_surface(
                maze_grid, known_pos, rows, cols, self._map_cell_px
            )
            self._fullscreen_cache_known = known_tuple
            self._fullscreen_cache_size = size_key
            self._fullscreen_cache_cell_px = self._map_cell_px

    def _clamp_map_camera(self, map_w, map_h):
        viewport_w = self.view_rect.width
        viewport_h = self.view_rect.height

        if map_w <= viewport_w:
            self._map_cam_x = -(viewport_w - map_w) / 2.0
        else:
            max_cam_x = map_w - viewport_w
            self._map_cam_x = min(max(0.0, self._map_cam_x), float(max_cam_x))

        if map_h <= viewport_h:
            self._map_cam_y = -(viewport_h - map_h) / 2.0
        else:
            max_cam_y = map_h - viewport_h
            self._map_cam_y = min(max(0.0, self._map_cam_y), float(max_cam_y))

    def _draw_fullscreen_map(self, maze_grid, player_pos, known_pos):
        if not maze_grid or not known_pos:
            self.screen.fill(COLOR_FULLSCREEN_BG)
            pygame.display.flip()
            # Feed empty data to the wait loop so it can still exit safely
            self._wait_for_map_close(maze_grid, known_pos, 0, 0, player_pos)
            return

        rows = len(maze_grid)
        cols = len(maze_grid[0]) if rows > 0 else 0
        if rows == 0 or cols == 0:
            self.screen.fill(COLOR_FULLSCREEN_BG)
            pygame.display.flip()
            self._wait_for_map_close(maze_grid, known_pos, rows, cols, player_pos)
            return

        # Reset zoom to default every time the map is toggled open
        self._map_cell_px = FULLSCREEN_CELL_PX
        self._update_fullscreen_cache(maze_grid, known_pos, rows, cols)

        map_w = cols * self._map_cell_px
        map_h = rows * self._map_cell_px

        if player_pos:
            px, py = player_pos
            self._map_cam_x = (py + 0.5) * self._map_cell_px - self.view_rect.width / 2
            self._map_cam_y = (px + 0.5) * self._map_cell_px - self.view_rect.height / 2
        else:
            self._map_cam_x = (map_w - self.view_rect.width) / 2
            self._map_cam_y = (map_h - self.view_rect.height) / 2

        self._clamp_map_camera(map_w, map_h)
        self._map_dragging = False

        self._render_fullscreen_frame(map_w, map_h, player_pos, rows, cols)
        pygame.display.flip()

        # Block and pass map context down to the loop so we can rebuild cache on zoom
        self._wait_for_map_close(maze_grid, known_pos, rows, cols, player_pos)

    def _render_fullscreen_frame(self, map_w, map_h, player_pos, rows, cols):
        self.screen.fill(COLOR_FULLSCREEN_BG)

        dest_x = self.view_rect.x - self._map_cam_x
        dest_y = self.view_rect.y - self._map_cam_y

        prev_clip = self.screen.get_clip()
        self.screen.set_clip(self.view_rect)
        self.screen.blit(self._fullscreen_cache_surface, (dest_x, dest_y))
        self.screen.set_clip(prev_clip)

        if player_pos:
            px, py = player_pos
            if 0 <= px < rows and 0 <= py < cols:
                screen_x = dest_x + (py + 0.5) * self._map_cell_px
                screen_y = dest_y + (px + 0.5) * self._map_cell_px
                radius = max(3, int(self._map_cell_px / 3))
                pygame.draw.circle(
                    self.screen, COLOR_MINIMAP_PLAYER,
                    (int(screen_x), int(screen_y)), radius,
                )

        pygame.draw.rect(self.screen, COLOR_MINIMAP_BORDER, self.view_rect, 2)

    def _wait_for_map_close(self, maze_grid, known_pos, rows, cols, player_pos):
        clock = pygame.time.Clock()
        waiting = True

        while waiting:
            redraw_needed = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                elif event.type == pygame.KEYDOWN and event.key == FULLSCREEN_MAP_KEY:
                    waiting = False
                    break

                # --- ZOOM LOGIC ---
                elif event.type == pygame.MOUSEWHEEL:
                    old_cell_px = self._map_cell_px
                    
                    # Adjust zoom by 2 pixels per scroll tick
                    self._map_cell_px += event.y * 2
                    self._map_cell_px = max(2, min(48, self._map_cell_px))

                    if self._map_cell_px != old_cell_px:
                        viewport_w = self.view_rect.width
                        viewport_h = self.view_rect.height

                        # Calculate the center of the screen in the *map's* coordinate space
                        center_map_x = self._map_cam_x + viewport_w / 2.0
                        center_map_y = self._map_cam_y + viewport_h / 2.0

                        # Scale that center point proportionally to the new zoom
                        ratio = self._map_cell_px / old_cell_px
                        new_center_map_x = center_map_x * ratio
                        new_center_map_y = center_map_y * ratio

                        # Shift the camera so the new center point remains in the middle of the screen
                        self._map_cam_x = new_center_map_x - viewport_w / 2.0
                        self._map_cam_y = new_center_map_y - viewport_h / 2.0

                        # Invalidate cache, rebuild with new zoom, and constrain camera bounds
                        self._update_fullscreen_cache(maze_grid, known_pos, rows, cols)
                        
                        map_w = cols * self._map_cell_px
                        map_h = rows * self._map_cell_px
                        self._clamp_map_camera(map_w, map_h)

                        redraw_needed = True

                # --- PAN LOGIC ---
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._map_dragging = True
                    self._map_drag_last_mouse = event.pos

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self._map_dragging = False

                elif event.type == pygame.MOUSEMOTION and self._map_dragging:
                    last_x, last_y = self._map_drag_last_mouse
                    dx = event.pos[0] - last_x
                    dy = event.pos[1] - last_y
                    self._map_drag_last_mouse = event.pos

                    self._map_cam_x -= dx
                    self._map_cam_y -= dy
                    
                    map_w = cols * self._map_cell_px
                    map_h = rows * self._map_cell_px
                    if map_w and map_h:
                        self._clamp_map_camera(map_w, map_h)
                    
                    redraw_needed = True

            if redraw_needed and rows > 0 and cols > 0:
                map_w = cols * self._map_cell_px
                map_h = rows * self._map_cell_px
                self._render_fullscreen_frame(map_w, map_h, player_pos, rows, cols)
                pygame.display.flip()

            clock.tick(60)

    # ── HUD: movement indicator & survival timer ────────────────────────

    def _draw_movement_indicator(self, player_walking):
        text = "Movement: Walking" if player_walking else "Movement: Sneaking"
        color = COLOR_HUD_WALK if player_walking else COLOR_HUD_SNEAK
        surf = self.fonts["hud"].render(text, True, color)
        pos = (self.view_rect.x + 10, self.view_rect.bottom - surf.get_height() - 10)
        self.screen.blit(surf, pos)
        
    def _draw_fps_counter(self, fps):
        text = f"FPS: {fps}"
        color = COLOR_TIMER_NORMAL
        surf = self.fonts["hud"].render(text, True, color)
        pos = (self.view_rect.x + 10, self.view_rect.y + 30)
        self.screen.blit(surf, pos)
        
    def _draw_map_tip(self):
        text = "Press M to open map"
        color = COLOR_HUD_SNEAK
        surf = self.fonts["hud"].render(text, True, color)
        pos = (self.view_rect.x + 600, self.view_rect.bottom - surf.get_height() - 10)
        self.screen.blit(surf, pos)

    def _draw_survival_timer(self, remaining_time):
        color = COLOR_TIMER_LOW if remaining_time <= 10 else COLOR_TIMER_NORMAL
        text = f"Time Remaining: {remaining_time}"
        surf = self.fonts["hud"].render(text, True, color)
        pos = (self.view_rect.x + 10, self.view_rect.y + 10)
        self.screen.blit(surf, pos)

    # ── Warning subtitles ────────────────────────────────────────────────

    def _draw_warning_subtitle(self):
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


def make_view_and_minimap_rects(cols, rows, margin=12,
                                max_minimap_w=150, max_minimap_h=150,
                                screen_w=None, screen_h=None,
                                size_min=10, size_max=450,
                                cell_px_min=4, cell_px_max=20):
    """
    Compute a `view_rect` and `minimap_rect` for a given maze size.

    - `cols`, `rows`: maze dimensions in cells (expected to already be
      clamped to [size_min, size_max] by the caller)
    - `margin`: outer margin in pixels
    - `max_minimap_w`, `max_minimap_h`: hard pixel caps for the minimap's
      width and height independently -- the minimap will never exceed
      either, regardless of maze aspect ratio.
    - `screen_w`, `screen_h`: optional screen size override. If omitted,
      attempts to use `SCREEN_WIDTH`/`SCREEN_HEIGHT` (imported from backbone).
    - `size_min`, `size_max`: known bounds for maze dimensions, used to
      scale cell_px smoothly (larger mazes -> smaller cells, automatically).
    - `cell_px_min`, `cell_px_max`: pixel-per-cell range to interpolate
      between as maze size moves across [size_min, size_max].

    Returns: (view_rect: pygame.Rect, minimap_rect: pygame.Rect)
    """
    if screen_w is None:
        screen_w = globals().get("SCREEN_WIDTH")
    if screen_h is None:
        screen_h = globals().get("SCREEN_HEIGHT")

    if screen_w is None or screen_h is None:
        raise RuntimeError("SCREEN_WIDTH/SCREEN_HEIGHT not found; pass screen_w/screen_h")

    # Smooth scaling based on the larger maze dimension (so a 450x10 maze
    # still gets small cells, not just a small *height*).
    larger_dim = max(cols, rows)
    span = max(1, size_max - size_min)
    t = (larger_dim - size_min) / span
    t = min(1.0, max(0.0, t))
    scaled_cell_px = cell_px_max - t * (cell_px_max - cell_px_min)

    # Independently cap cell_px so NEITHER axis can exceed its own pixel
    # budget, regardless of aspect ratio. This is the key fix: width and
    # height are each bounded on their own terms, not via a shared
    # "fits in a square box" assumption.
    fit_cell_w = max_minimap_w / max(1, cols)
    fit_cell_h = max_minimap_h / max(1, rows)
    fit_cell_px = min(fit_cell_w, fit_cell_h)

    cell_px = max(cell_px_min, min(scaled_cell_px, fit_cell_px))
    cell_px = int(round(cell_px))
    cell_px = max(1, cell_px)  # never let rounding collapse it to 0

    minimap_w = cols * cell_px
    minimap_h = rows * cell_px

    # Belt-and-suspenders: even after the above, clamp directly to the
    # pixel caps (handles rounding overshoot) and to the screen-fraction cap.
    minimap_w = min(minimap_w, max_minimap_w, max(64, screen_w // 3))
    minimap_h = min(minimap_h, max_minimap_h, max(64, screen_h // 3))

    minimap_rect = pygame.Rect(screen_w - margin - minimap_w, margin, minimap_w, minimap_h)
    view_rect = pygame.Rect(0, 0, screen_w, screen_h)

    return view_rect, minimap_rect


def create_visual_effects(cols, rows, margin=12, max_minimap_px=150):
    """Convenience factory: compute rects from maze size and return a VisualEffects instance."""
    vrect, mrect = make_view_and_minimap_rects(cols, rows, margin, max_minimap_px)
    return VisualEffects(vrect, mrect)