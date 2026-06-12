import pygame
import sys
from .interface.backbone import *
from .gameplay import game_screen
from ..generation.generate_all import generate

def play_menu(start_t=0.0):
    PANEL_W, PANEL_H = 480, 430
    PANEL_X = (SCREEN_WIDTH  - PANEL_W) // 2
    PANEL_Y = (SCREEN_HEIGHT - PANEL_H) // 2 - 10
    PAD_L   = PANEL_X + 30       
    IW      = PANEL_W - 60       
    IH      = 38                  
    HALF_W  = (IW - 16) // 2     

    TITLE_BAR_H = 48              
    Y_ALGO      = PANEL_Y + TITLE_BAR_H + 28   
    Y_HEURISTIC = Y_ALGO + IH + 30
    Y_INPUTS_NO_HEUR = Y_HEURISTIC          
    Y_INPUTS_HEUR    = Y_HEURISTIC + IH + 30  
    Y_WALL_OFFSET    = IH + 30              

    algo_dd      = Dropdown(PAD_L, Y_ALGO, IW, IH, "ALGORITHM",
                            ["DFS", "BFS", "Greedy Best-First Search", "A*", "Bidirectional BFS"])
    heuristic_dd = Dropdown(PAD_L, Y_HEURISTIC, IW, IH, "HEURISTIC",
                            ["Euclidean", "Manhattan"])

    rows_input = IntInputBox(PAD_L,                  0, HALF_W, IH, "ROWS",    default=10)
    cols_input = IntInputBox(PAD_L + HALF_W + 16,    0, HALF_W, IH, "COLUMNS", default=10)
    wall_input = FloatInputBox(PAD_L,                0, IW,     IH,
                               "WALL DENSITY  [ 0 – 1 ]", default="0.3")

    start_btn = NeonButton(SCREEN_WIDTH // 2, PANEL_Y + PANEL_H - 58, "> START GAME",
                           NEON_GREEN, DIM_GREEN)
    back_btn  = NeonButton(SCREEN_WIDTH // 2, PANEL_Y + PANEL_H - 18, "> BACK",
                           NEON_PURPLE, (65, 0, 95))

    t           = start_t
    blurred_bg  = None
    last_bg_t   = -999.0
    BG_REFRESH  = 2.0

    running = True
    go_back = False

    while running:
        dt = clock.tick(FPS) / 1000.0
        t += dt
        mouse_pos = pygame.mouse.get_pos()
        show_heuristic = algo_dd.value in ALGOS_WITH_HEURISTIC

        iy = Y_INPUTS_HEUR if show_heuristic else Y_INPUTS_NO_HEUR
        rows_input.rect.y = iy
        cols_input.rect.y = iy
        wall_input.rect.y = iy + Y_WALL_OFFSET

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_btn.is_clicked(mouse_pos):
                    go_back = True
                    running = False
                    break
                elif start_btn.is_clicked(mouse_pos):
                    rows = rows_input.value
                    cols = cols_input.value
                    wall = wall_input.value
                    algo = algo_dd.value
                    heur = heuristic_dd.value if show_heuristic else None
                    if rows and cols and wall is not None:
                        start, goal, maze = generate(rows, cols, wall)
                        running = False
                        game_screen(maze, rows, cols, algo, heur, wall, start, goal, t)
                    else:
                        if not rows_input.value: rows_input.error = True
                        if not cols_input.value: cols_input.error = True
                        if wall_input.value is None: wall_input.error = True

            algo_consumed = algo_dd.handle_event(event, mouse_pos)
            if algo_consumed:
                heuristic_dd.close()
            else:
                if show_heuristic and not algo_dd.open:
                    heuristic_dd.handle_event(event, mouse_pos)
                if not algo_dd.open and not (show_heuristic and heuristic_dd.open):
                    rows_input.handle_event(event, mouse_pos)
                    cols_input.handle_event(event, mouse_pos)
                    wall_input.handle_event(event, mouse_pos)

        algo_dd.update(mouse_pos)
        if show_heuristic:
            heuristic_dd.update(mouse_pos)
        else:
            heuristic_dd.close()   

        rows_input.update(dt)
        cols_input.update(dt)
        wall_input.update(dt)
        start_btn.update(mouse_pos, dt)
        back_btn.update(mouse_pos, dt)

        if blurred_bg is None or (t - last_bg_t) > BG_REFRESH:
            blurred_bg = build_blurred_bg(t)
            last_bg_t  = t

        screen.blit(blurred_bg, (0, 0))

        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 70))
        screen.blit(dim, (0, 0))

        draw_corner_decorations(screen, t)

        panel_bg = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
        panel_bg.fill((0, 22, 20, 210))
        pygame.draw.rect(panel_bg, (*NEON_CYAN, 55), panel_bg.get_rect(), 2, border_radius=10)
        screen.blit(panel_bg, (PANEL_X, PANEL_Y))

        title_s = font_sub.render("NEW GAME", True, NEON_CYAN)
        screen.blit(title_s, title_s.get_rect(centerx=SCREEN_WIDTH // 2, y=PANEL_Y + 14))
        sep_y = PANEL_Y + 40
        sep_s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(sep_s, (*NEON_CYAN, 60),
                         (PANEL_X + 16, sep_y), (PANEL_X + PANEL_W - 16, sep_y), 1)
        screen.blit(sep_s, (0, 0))

        rows_input.draw(screen)
        cols_input.draw(screen)
        wall_input.draw(screen)

        if show_heuristic and not algo_dd.open:
            heuristic_dd.draw(screen)

        algo_dd.draw(screen)
        start_btn.draw(screen)
        back_btn.draw(screen)

        screen.blit(SCANLINE_SURF, (0, 0))
        pygame.display.flip()

    if go_back:
        # Local import prevents circular dependency!
        from .interface.main_menu import main_menu
        main_menu()