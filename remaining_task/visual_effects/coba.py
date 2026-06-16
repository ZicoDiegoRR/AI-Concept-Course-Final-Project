import pygame
import math

# ── Tunable layout / style constants ────────────────────────────────────────

CELL_SIZE = 40          # size in px of a maze cell in the main view
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

    def __init__(self, screen, fonts, view_rect, minimap_rect):
        """
        screen:        pygame display surface
        fonts:         dict with keys "hud", "label", "sub" (pygame Font objects)
        view_rect:     pygame.Rect, the main gameplay viewport on screen
        minimap_rect:  pygame.Rect, where to draw the minimap
        """
        self.screen = screen
        self.fonts = fonts
        self.view_rect = view_rect
        self.minimap_rect = minimap_rect

        # Warning subtitle timers (seconds remaining to display)
        self._see_warning_timer = 0.0
        self._hear_warning_timer = 0.0

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

            7. Minimap
            6. Maze Cells
            5. Maze Walls
            4. Gameplay Objects (hiding spots, agent, player)
            3. Movement Indicator
            2. Survival Timer
            1. Warning Subtitle
        """
        player_vision = set(visual_dict.get("player_vision", []))

        self._draw_minimap(visual_dict.get("player_known_map", []),
                           visual_dict.get("player_pos"))

        self._draw_maze_cells(visual_dict, player_vision)
        self._draw_maze_walls(visual_dict, player_vision)
        self._draw_gameplay_objects(visual_dict, player_vision)

        self._draw_movement_indicator(visual_dict.get("player_walking", False))
        self._draw_survival_timer(visual_dict.get("remaining_time", 0))

        self._draw_warning_subtitle()

    # ── Field of view rendering ─────────────────────────────────────────

    def _cell_to_screen(self, cell, view_origin):
        """Convert a maze cell coordinate to a top-left screen pixel position."""
        cx, cy = cell
        ox, oy = view_origin
        sx = self.view_rect.x + (cx - ox) * CELL_SIZE
        sy = self.view_rect.y + (cy - oy) * CELL_SIZE
        return sx, sy

    def _is_visible(self, cell, player_vision):
        return cell in player_vision

    def _draw_maze_cells(self, visual_dict, player_vision):
        """Draw only the floor cells that are within the player's vision."""
        view_origin = visual_dict.get("view_origin", (0, 0))

        # Fill viewport with fog as a base layer
        fog = pygame.Surface(self.view_rect.size)
        fog.fill(COLOR_FOG)
        self.screen.blit(fog, self.view_rect.topleft)

        for cell in player_vision:
            sx, sy = self._cell_to_screen(cell, view_origin)
            rect = pygame.Rect(sx, sy, CELL_SIZE, CELL_SIZE)
            if not self.view_rect.colliderect(rect):
                continue
            pygame.draw.rect(self.screen, COLOR_CELL_FLOOR, rect)

    def _draw_maze_walls(self, visual_dict, player_vision):
        """Draw walls, but only for cells inside the player's vision."""
        maze_grid = visual_dict.get("maze_grid")
        if not maze_grid:
            return
        view_origin = visual_dict.get("view_origin", (0, 0))

        for cell in player_vision:
            cx, cy = cell
            if cy < 0 or cy >= len(maze_grid):
                continue
            row = maze_grid[cy]
            if cx < 0 or cx >= len(row):
                continue

            cell_data = row[cx]
            walls = cell_data.get("walls", {})
            sx, sy = self._cell_to_screen(cell, view_origin)
            rect = pygame.Rect(sx, sy, CELL_SIZE, CELL_SIZE)
            if not self.view_rect.colliderect(rect):
                continue

            if walls.get("N"):
                pygame.draw.line(self.screen, COLOR_WALL,
                                  (sx, sy), (sx + CELL_SIZE, sy), WALL_THICKNESS)
            if walls.get("S"):
                pygame.draw.line(self.screen, COLOR_WALL,
                                  (sx, sy + CELL_SIZE), (sx + CELL_SIZE, sy + CELL_SIZE), WALL_THICKNESS)
            if walls.get("W"):
                pygame.draw.line(self.screen, COLOR_WALL,
                                  (sx, sy), (sx, sy + CELL_SIZE), WALL_THICKNESS)
            if walls.get("E"):
                pygame.draw.line(self.screen, COLOR_WALL,
                                  (sx + CELL_SIZE, sy), (sx + CELL_SIZE, sy + CELL_SIZE), WALL_THICKNESS)

    def _draw_gameplay_objects(self, visual_dict, player_vision):
        """Draw hiding spots, agent, and player -- only if their cell is visible."""
        maze_grid = visual_dict.get("maze_grid")
        view_origin = visual_dict.get("view_origin", (0, 0))

        # Hiding spots
        if maze_grid:
            for cell in player_vision:
                cx, cy = cell
                if cy < 0 or cy >= len(maze_grid):
                    continue
                row = maze_grid[cy]
                if cx < 0 or cx >= len(row):
                    continue
                if row[cx].get("hiding_spot"):
                    sx, sy = self._cell_to_screen(cell, view_origin)
                    rect = pygame.Rect(sx + 6, sy + 6, CELL_SIZE - 12, CELL_SIZE - 12)
                    if self.view_rect.colliderect(rect):
                        pygame.draw.rect(self.screen, COLOR_HIDING_SPOT, rect, border_radius=4)

        # Agent (only render if its cell is within player vision)
        agent_pos = visual_dict.get("agent_pos")
        if agent_pos and self._is_visible(agent_pos, player_vision):
            sx, sy = self._cell_to_screen(agent_pos, view_origin)
            center = (sx + CELL_SIZE // 2, sy + CELL_SIZE // 2)
            if self.view_rect.collidepoint(center):
                pygame.draw.circle(self.screen, COLOR_AGENT, center, CELL_SIZE // 3)

        # Player (rendered if its own cell is visible -- normally always true)
        player_pos = visual_dict.get("player_pos")
        if player_pos and self._is_visible(player_pos, player_vision):
            sx, sy = self._cell_to_screen(player_pos, view_origin)
            center = (sx + CELL_SIZE // 2, sy + CELL_SIZE // 2)
            if self.view_rect.collidepoint(center):
                pygame.draw.circle(self.screen, COLOR_PLAYER, center, CELL_SIZE // 3)

    # ── Minimap ──────────────────────────────────────────────────────────

    def _draw_minimap(self, known_map, player_pos):
        """
        Draw the fog-of-war minimap. Known cells are shown, unknown cells
        are rendered as fog. Player position is marked if known.
        """
        rect = self.minimap_rect
        pygame.draw.rect(self.screen, COLOR_MINIMAP_BG, rect)
        pygame.draw.rect(self.screen, COLOR_MINIMAP_BORDER, rect, 2, border_radius=2)

        if not known_map or not known_map[0]:
            return

        rows = len(known_map)
        cols = len(known_map[0])

        cell_w = rect.width / cols
        cell_h = rect.height / rows

        for y in range(rows):
            for x in range(cols):
                cell_rect = pygame.Rect(
                    rect.x + x * cell_w,
                    rect.y + y * cell_h,
                    math.ceil(cell_w),
                    math.ceil(cell_h),
                )
                if known_map[y][x]:
                    pygame.draw.rect(self.screen, COLOR_MINIMAP_KNOWN, cell_rect)
                else:
                    pygame.draw.rect(self.screen, COLOR_MINIMAP_FOG, cell_rect)

        if player_pos:
            px, py = player_pos
            if 0 <= py < rows and 0 <= px < cols:
                center = (
                    int(rect.x + (px + 0.5) * cell_w),
                    int(rect.y + (py + 0.5) * cell_h),
                )
                radius = max(2, int(min(cell_w, cell_h) / 2))
                pygame.draw.circle(self.screen, COLOR_MINIMAP_PLAYER, center, radius)

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