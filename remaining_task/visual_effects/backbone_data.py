import pygame
import sys
import math

pygame.init()

SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
FPS = 60

# Neon color palette
WHITE       = (255, 255, 255)
NEON_CYAN   = (0, 255, 220)
NEON_PINK   = (255, 0, 180)
NEON_PURPLE = (180, 0, 255)
DIM_CYAN    = (0, 80, 72)
DIM_PINK    = (80, 0, 56)
NEON_GREEN  = (0, 255, 120)
DIM_GREEN   = (0, 80, 40)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("HnS: Hide & Seek Game")
clock = pygame.time.Clock()

font_title  = pygame.font.SysFont("couriernew", 80, bold=True)
font_button = pygame.font.SysFont("couriernew", 38, bold=True)
font_sub    = pygame.font.SysFont("couriernew", 20, bold=True)
font_label  = pygame.font.SysFont("couriernew", 17, bold=True)
font_input  = pygame.font.SysFont("couriernew", 20, bold=True)
font_hud    = pygame.font.SysFont("couriernew", 16, bold=True)

# ── Shared rendering helpers ─────────────────────────────────────────────────

def make_glow_surface(text, font, color, glow_alpha, padding=40):
    text_surf = font.render(text, True, color)
    tw, th = text_surf.get_size()
    canvas_w = tw + padding * 2
    canvas_h = th + padding * 2
    canvas = pygame.Surface((canvas_w, canvas_h), pygame.SRCALPHA)
    canvas.blit(text_surf, (padding, padding))
    small_w = max(canvas_w // 2, 1)
    small_h = max(canvas_h // 2, 1)
    small = pygame.transform.smoothscale(canvas, (small_w, small_h))
    bloom = pygame.transform.smoothscale(small, (canvas_w, canvas_h))
    bloom.set_alpha(glow_alpha)
    return bloom, text_surf, padding

def draw_neon_text(surface, text, font, color, center_pos, glow_alpha=90):
    padding = 48
    bloom, text_surf, pad = make_glow_surface(text, font, color, glow_alpha, padding)
    bw, bh = bloom.get_size()
    surface.blit(bloom, (center_pos[0] - bw // 2, center_pos[1] - bh // 2))
    bloom2, _, _ = make_glow_surface(text, font, color, glow_alpha // 2, padding * 2)
    bw2, bh2 = bloom2.get_size()
    surface.blit(bloom2, (center_pos[0] - bw2 // 2, center_pos[1] - bh2 // 2))
    core_color = tuple(min(255, int(c * 0.15 + 255 * 0.85)) for c in color)
    core = font.render(text, True, core_color)
    surface.blit(core, core.get_rect(center=center_pos))

def draw_grid(surface, t):
    grid_color = (0, 45, 38)
    vanish_x = SCREEN_WIDTH // 2
    horizon   = SCREEN_HEIGHT // 2 + 40
    for i in range(-14, 15):
        base_x = vanish_x + i * 58
        pygame.draw.line(surface, grid_color, (vanish_x, horizon), (base_x, SCREEN_HEIGHT), 1)
    for j in range(12):
        progress = (j / 11) ** 2
        y = int(horizon + progress * (SCREEN_HEIGHT - horizon))
        x_spread = int(progress * SCREEN_WIDTH * 0.72)
        pygame.draw.line(surface, grid_color,
                         (vanish_x - x_spread, y), (vanish_x + x_spread, y), 1)

def draw_corner_decorations(surface, t):
    size = 32
    alpha = int(150 + 90 * math.sin(t * 2))
    corners = [
        (22, 22,  1,  1),
        (SCREEN_WIDTH - 22, 22, -1,  1),
        (22, SCREEN_HEIGHT - 22,  1, -1),
        (SCREEN_WIDTH - 22, SCREEN_HEIGHT - 22, -1, -1),
    ]
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for (cx, cy, sx, sy) in corners:
        pygame.draw.line(s, (*NEON_CYAN, alpha), (cx, cy), (cx + sx * size, cy), 2)
        pygame.draw.line(s, (*NEON_CYAN, alpha), (cx, cy), (cx, cy + sy * size), 2)
    surface.blit(s, (0, 0))

def blur_surface(surf, passes=2):
    w, h = surf.get_size()
    s = surf.copy()
    for _ in range(passes):
        small = pygame.transform.smoothscale(s, (w // 2, h // 2))
        s = pygame.transform.smoothscale(small, (w, h))
    return s

# ── Pre-baked surfaces ───────────────────────────────────────────────────────
SCANLINE_SURF = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
for _y in range(0, SCREEN_HEIGHT, 3):
    pygame.draw.line(SCANLINE_SURF, (0, 0, 0, 22), (0, _y), (SCREEN_WIDTH, _y))

VIGNETTE_SURF = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
for _r in range(440, 0, -10):
    _a = max(0, int((1 - _r / 440) * 100))
    pygame.draw.circle(VIGNETTE_SURF, (0, 0, 0, _a),
                       (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), _r)

def draw_background(surface, t):
    surface.fill((2, 4, 8))
    draw_grid(surface=surface, t=t)
    surface.blit(VIGNETTE_SURF, (0, 0))
    draw_corner_decorations(surface, t)

def build_blurred_bg(t):
    tmp = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    draw_background(tmp, t)
    return blur_surface(tmp, passes=2) 

# ── UI Classes ───────────────────────────────────────────────────────────────

BORDER_IDLE   = (0, 120, 110)
BORDER_ACTIVE = (0, 255, 220)
BORDER_ERR    = (255, 50, 80)
BG_WIDGET     = (5, 18, 16)
TEXT_COLOR    = (200, 255, 248)
LABEL_COLOR   = (0, 180, 160)
DROPDOWN_HIGH = (0, 40, 36)

def _draw_neon_border(surface, rect, color, alpha=200, width=2):
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), rect, width, border_radius=4)
    surface.blit(s, (0, 0))

def _draw_label(surface, text, rect):
    lbl = font_label.render(text, True, LABEL_COLOR)
    surface.blit(lbl, (rect.x, rect.y - 22))

class NeonButton:
    def __init__(self, x, y, text, color_main, color_dim):
        self.cx = x
        self.cy = y
        self.text = text
        self.color_main = color_main
        self.color_dim  = color_dim
        self.is_hovered = False
        self._t = 0.0

    def get_rect(self):
        surf = font_button.render(self.text, True, WHITE)
        return surf.get_rect(center=(self.cx, self.cy)).inflate(50, 24)

    def update(self, mouse_pos, dt):
        self.is_hovered = self.get_rect().collidepoint(mouse_pos)
        self._t += dt

    def draw(self, surface):
        if self.is_hovered:
            pulse      = 0.5 + 0.5 * math.sin(self._t * 4.5)
            glow_alpha = int(70 + pulse * 60)
            color      = self.color_main
        else:
            glow_alpha = 40
            color      = self.color_dim
        draw_neon_text(surface, self.text, font_button, color,
                       (self.cx, self.cy), glow_alpha=glow_alpha)

    def is_clicked(self, mouse_pos):
        return self.get_rect().collidepoint(mouse_pos)

class Dropdown:
    def __init__(self, x, y, w, h, label, options):
        self.rect    = pygame.Rect(x, y, w, h)
        self.label   = label
        self.options = options
        self.selected_idx = 0
        self.open    = False
        self._hovered_idx = -1

    @property
    def value(self): return self.options[self.selected_idx]

    def close(self): self.open = False

    def _option_rect(self, i):
        return pygame.Rect(self.rect.x, self.rect.bottom + i * self.rect.h, self.rect.w, self.rect.h)

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.open = not self.open
                return True
            if self.open:
                for i in range(len(self.options)):
                    if self._option_rect(i).collidepoint(mouse_pos):
                        self.selected_idx = i
                        self.open = False
                        return True
                self.open = False
        return False

    def update(self, mouse_pos):
        self._hovered_idx = -1
        if self.open:
            for i in range(len(self.options)):
                if self._option_rect(i).collidepoint(mouse_pos):
                    self._hovered_idx = i

    def draw(self, surface, clip_rect=None):
        border_col = BORDER_ACTIVE if self.open else BORDER_IDLE
        _draw_label(surface, self.label, self.rect)
        pygame.draw.rect(surface, BG_WIDGET, self.rect, border_radius=4)
        _draw_neon_border(surface, self.rect, border_col)
        txt = font_input.render(self.value, True, TEXT_COLOR)
        surface.blit(txt, txt.get_rect(midleft=(self.rect.x + 12, self.rect.centery)))
        arrow = "▲" if self.open else "▼"
        arr_s = font_label.render(arrow, True, border_col)
        surface.blit(arr_s, arr_s.get_rect(midright=(self.rect.right - 10, self.rect.centery)))

        if self.open:
            panel_h = len(self.options) * self.rect.h
            panel_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.w, panel_h)
            pygame.draw.rect(surface, (4, 14, 12), panel_rect, border_radius=4)
            _draw_neon_border(surface, panel_rect, BORDER_ACTIVE)
            for i, opt in enumerate(self.options):
                r = self._option_rect(i)
                if i == self._hovered_idx:
                    pygame.draw.rect(surface, DROPDOWN_HIGH, r, border_radius=2)
                col = NEON_CYAN if (i == self.selected_idx) else TEXT_COLOR
                t = font_input.render(opt, True, col)
                surface.blit(t, t.get_rect(midleft=(r.x + 12, r.centery)))

class IntInputBox:
    def __init__(self, x, y, w, h, label, default="", allow_negative=False):
        self.rect  = pygame.Rect(x, y, w, h)
        self.label = label
        self.text  = str(default)
        self.active = False
        self.allow_negative = allow_negative
        self.error  = False
        self._cursor_t = 0.0

    @property
    def value(self):
        try: return int(self.text)
        except ValueError: return None

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(mouse_pos)
            self.error  = False
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit():
                self.text += event.unicode
            elif event.unicode == '-' and self.allow_negative and self.text == '':
                self.text = '-'
            self.error = (self.value is None and self.text not in ('', '-'))

    def update(self, dt): self._cursor_t += dt

    def draw(self, surface):
        border_col = BORDER_ERR if self.error else (BORDER_ACTIVE if self.active else BORDER_IDLE)
        _draw_label(surface, self.label, self.rect)
        pygame.draw.rect(surface, BG_WIDGET, self.rect, border_radius=4)
        _draw_neon_border(surface, self.rect, border_col)
        display = self.text
        if self.active and int(self._cursor_t * 2) % 2 == 0:
            display += "|"
        txt = font_input.render(display, True, TEXT_COLOR)
        surface.blit(txt, txt.get_rect(midleft=(self.rect.x + 12, self.rect.centery)))

class FloatInputBox:
    def __init__(self, x, y, w, h, label, default=""):
        self.rect   = pygame.Rect(x, y, w, h)
        self.label  = label
        self.text   = str(default)
        self.active = False
        self.error  = False
        self._cursor_t = 0.0

    @property
    def value(self):
        try:
            v = float(self.text)
            return v if 0.0 <= v <= 1.0 else None
        except ValueError: return None

    def _is_valid_partial(self, s):
        if s in ('', '0', '1', '.', '0.', '1.'): return True
        try:
            v = float(s)
            return 0.0 <= v <= 1.0
        except ValueError: return False

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(mouse_pos)
            self.error  = False
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                self.error = False
            elif event.unicode in '0123456789.':
                candidate = self.text + event.unicode
                if self._is_valid_partial(candidate):
                    self.text = candidate
                else:
                    self.error = True
            self.error = not self._is_valid_partial(self.text)

    def update(self, dt): self._cursor_t += dt

    def draw(self, surface):
        border_col = BORDER_ERR if self.error else (BORDER_ACTIVE if self.active else BORDER_IDLE)
        _draw_label(surface, self.label, self.rect)
        pygame.draw.rect(surface, BG_WIDGET, self.rect, border_radius=4)
        _draw_neon_border(surface, self.rect, border_col)
        display = self.text
        if self.active and int(self._cursor_t * 2) % 2 == 0:
            display += "|"
        txt = font_input.render(display, True, TEXT_COLOR)
        surface.blit(txt, txt.get_rect(midleft=(self.rect.x + 12, self.rect.centery)))