import pygame
import sys
import math
from .backbone import *
from .play_menu import play_menu

def main_menu():
    buttons = [
        NeonButton(SCREEN_WIDTH // 2, 335, "> PLAY", NEON_CYAN, DIM_CYAN),
        NeonButton(SCREEN_WIDTH // 2, 405, "> SETTINGS", NEON_GREEN, DIM_GREEN),
        NeonButton(SCREEN_WIDTH // 2, 475, "> QUIT", NEON_PURPLE, (65, 0, 95)),
    ]

    t = 0.0
    running = True
    next_screen = None

    while running:
        dt = clock.tick(FPS) / 1000.0
        t += dt
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if buttons[0].is_clicked(mouse_pos):
                    next_screen = "play"
                    running = False
                if buttons[1].is_clicked(mouse_pos):
                    print("Settings clicked!")
                elif buttons[2].is_clicked(mouse_pos):
                    pygame.quit(); sys.exit()

        for btn in buttons:
            btn.update(mouse_pos, dt)

        screen.fill((2, 4, 8))
        draw_grid(surface=screen, t=t)
        screen.blit(VIGNETTE_SURF, (0, 0))
        draw_corner_decorations(screen, t)

        # ── Titles ──────────────────────────────────────────────────
        title_pulse = 0.5 + 0.5 * math.sin(t * 1.4)
        draw_neon_text(screen, "H n S:", font_title, NEON_CYAN,
                       (SCREEN_WIDTH // 2, 108), glow_alpha=int(70 + title_pulse * 55))

        # "Hide &" in pink, "Seek" in cyan — rendered as one visual line
        hs_left  = font_title.render("Hide", True, NEON_PINK)
        hs_middle = font_title.render(" & ", True, NEON_PURPLE)
        hs_right = font_title.render("Seek", True, NEON_CYAN)
        total_w  = hs_left.get_width() + hs_middle.get_width() + hs_right.get_width()
        tx = SCREEN_WIDTH // 2 - total_w // 2
        screen.blit(hs_left,  (tx, 150))
        screen.blit(hs_middle, (tx + hs_left.get_width(), 150))
        screen.blit(hs_right, (tx + hs_middle.get_width() + hs_left.get_width(), 150))

        # ── Subtitle ────────────────────────────────────────────────
        sub_alpha = int(180 + 60 * math.sin(t * 1.0))
        sub_surf = font_sub.render("[ don't get caught by it! ]", True, (0, 200, 175))
        sub_surf.set_alpha(sub_alpha)
        screen.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 258)))

        for btn in buttons:
            btn.draw(screen)

        screen.blit(SCANLINE_SURF, (0, 0))
        pygame.display.flip()

    if next_screen == "play":
        play_menu(t)

if __name__ == "__main__":
    main_menu()