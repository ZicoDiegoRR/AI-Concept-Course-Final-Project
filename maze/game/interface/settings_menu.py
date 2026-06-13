import pygame
import sys
from .backbone import *

def settings_menu(init_state=None, start_t=0.0):

    PANEL_W, PANEL_H = 540, 500
    PANEL_X = (SCREEN_WIDTH - PANEL_W) // 2
    PANEL_Y = (SCREEN_HEIGHT - PANEL_H) // 2 - 10

    PAD_L = PANEL_X + 30
    IW = PANEL_W - 60
    IH = 38

    RGB_W = (IW - 20) // 3
    
    if not init_state:
        INIT_STATE = {
            "player_color": (
                0,
                255,
                220,
            ),
            "agent_color": (
                255,
                0,
                180,
            ),
            "agent_heuristic": "Euclidean"
        }
    else:
        INIT_STATE = init_state

    # ==========================================================
    # PLAYER COLOR
    # ==========================================================
    player_color_yoffset = 105

    player_r = IntInputBox(
        PAD_L,
        PANEL_Y + player_color_yoffset,
        RGB_W,
        IH,
        "PLAYER R",
        default=INIT_STATE["player_color"][0]
    )

    player_g = IntInputBox(
        PAD_L + RGB_W + 10,
        PANEL_Y + player_color_yoffset,
        RGB_W,
        IH,
        "PLAYER G",
        default=INIT_STATE["player_color"][1]
    )

    player_b = IntInputBox(
        PAD_L + (RGB_W + 10) * 2,
        PANEL_Y + player_color_yoffset,
        RGB_W,
        IH,
        "PLAYER B",
        default=INIT_STATE["player_color"][2]
    )

    # ==========================================================
    # AGENT COLOR
    # ==========================================================
    agent_color_yoffset = 245

    agent_r = IntInputBox(
        PAD_L,
        PANEL_Y + agent_color_yoffset,
        RGB_W,
        IH,
        "AGENT R",
        default=INIT_STATE["agent_color"][0]
    )

    agent_g = IntInputBox(
        PAD_L + RGB_W + 10,
        PANEL_Y + agent_color_yoffset,
        RGB_W,
        IH,
        "AGENT G",
        default=INIT_STATE["agent_color"][1]
    )

    agent_b = IntInputBox(
        PAD_L + (RGB_W + 10) * 2,
        PANEL_Y + agent_color_yoffset,
        RGB_W,
        IH,
        "AGENT B",
        default=INIT_STATE["agent_color"][2]
    )

    # ==========================================================
    # HEURISTIC
    # ==========================================================

    heuristic_dd = Dropdown(
        PAD_L,
        PANEL_Y + 355,
        IW,
        IH,
        "AGENT HEURISTIC",
        [
            "Euclidean",
            "Manhattan"
        ][::1 if INIT_STATE["agent_heuristic"] == "Euclidean" else -1],
    )

    # ==========================================================
    # BUTTONS
    # ==========================================================

    back_btn = NeonButton(
        SCREEN_WIDTH // 2,
        PANEL_Y + PANEL_H - 40,
        "> BACK",
        NEON_PURPLE,
        (65, 0, 95)
    )

    # ==========================================================
    # BACKGROUND CACHE
    # ==========================================================

    t = start_t

    blurred_bg = None
    last_bg_t = -999.0
    BG_REFRESH = 2.0

    running = True

    while running:

        dt = clock.tick(FPS) / 1000.0
        t += dt

        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                if back_btn.is_clicked(mouse_pos) and not heuristic_dd.open:

                    def clamp(v):
                        if v is None:
                            return 0
                        return max(0, min(255, v))

                    state_dict = {
                        "state": 0,
                        "settings_dict": {
                            "player_color": (
                                clamp(player_r.value),
                                clamp(player_g.value),
                                clamp(player_b.value)
                            ),
                            "agent_color": (
                                clamp(agent_r.value),
                                clamp(agent_g.value),
                                clamp(agent_b.value)
                            ),
                            "agent_heuristic": heuristic_dd.value
                        }
                    }

                    return state_dict

            heuristic_dd.handle_event(event, mouse_pos)

            if not heuristic_dd.open:

                player_r.handle_event(event, mouse_pos)
                player_g.handle_event(event, mouse_pos)
                player_b.handle_event(event, mouse_pos)

                agent_r.handle_event(event, mouse_pos)
                agent_g.handle_event(event, mouse_pos)
                agent_b.handle_event(event, mouse_pos)

        heuristic_dd.update(mouse_pos)

        player_r.update(dt)
        player_g.update(dt)
        player_b.update(dt)

        agent_r.update(dt)
        agent_g.update(dt)
        agent_b.update(dt)

        back_btn.update(mouse_pos, dt)

        if blurred_bg is None or (t - last_bg_t) > BG_REFRESH:
            blurred_bg = build_blurred_bg(t)
            last_bg_t = t

        screen.blit(blurred_bg, (0, 0))

        dim = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SRCALPHA
        )
        dim.fill((0, 0, 0, 70))
        screen.blit(dim, (0, 0))

        draw_corner_decorations(screen, t)

        # ======================================================
        # PANEL
        # ======================================================

        panel_bg = pygame.Surface(
            (PANEL_W, PANEL_H),
            pygame.SRCALPHA
        )

        panel_bg.fill((0, 22, 20, 210))

        pygame.draw.rect(
            panel_bg,
            (*NEON_CYAN, 55),
            panel_bg.get_rect(),
            2,
            border_radius=10
        )

        screen.blit(panel_bg, (PANEL_X, PANEL_Y))

        title_s = font_sub.render(
            "SETTINGS",
            True,
            NEON_CYAN
        )

        screen.blit(
            title_s,
            title_s.get_rect(
                centerx=SCREEN_WIDTH // 2,
                y=PANEL_Y + 14
            )
        )

        sep_y = PANEL_Y + 40

        sep_s = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.SRCALPHA
        )

        pygame.draw.line(
            sep_s,
            (*NEON_CYAN, 60),
            (PANEL_X + 16, sep_y),
            (PANEL_X + PANEL_W - 16, sep_y),
            1
        )

        screen.blit(sep_s, (0, 0))

        # ======================================================
        # SECTION LABELS
        # ======================================================

        player_lbl = font_sub.render(
            "PLAYER COLOR",
            True,
            NEON_CYAN
        )

        screen.blit(
            player_lbl,
            (PAD_L, PANEL_Y + 55)
        )

        agent_lbl = font_sub.render(
            "AGENT COLOR",
            True,
            NEON_CYAN
        )

        screen.blit(
            agent_lbl,
            (PAD_L, PANEL_Y + 195)
        )

        # ======================================================
        # COLOR PREVIEW
        # ======================================================

        pygame.draw.rect(
            screen,
            (
                max(0, min(255, player_r.value or 0)),
                max(0, min(255, player_g.value or 0)),
                max(0, min(255, player_b.value or 0))
            ),
            (PAD_L, PANEL_Y + 155, 80, 25),
            border_radius=4
        )

        pygame.draw.rect(
            screen,
            (
                max(0, min(255, agent_r.value or 0)),
                max(0, min(255, agent_g.value or 0)),
                max(0, min(255, agent_b.value or 0))
            ),
            (PAD_L, PANEL_Y + 295, 80, 25),
            border_radius=4
        )

        player_r.draw(screen)
        player_g.draw(screen)
        player_b.draw(screen)

        agent_r.draw(screen)
        agent_g.draw(screen)
        agent_b.draw(screen)

        heuristic_dd.draw(screen)

        if not heuristic_dd.open:
            back_btn.draw(screen)

        screen.blit(SCANLINE_SURF, (0, 0))

        pygame.display.flip()