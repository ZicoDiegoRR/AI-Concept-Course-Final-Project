import pygame
import sys
from hns_maze.game.interface.backbone import *

def play_menu(start_t=0.0):
    # --- 1. Dimensi Panel & Layouting Dua Kolom ---
    PANEL_W, PANEL_H = 740, 480
    PANEL_X = (SCREEN_WIDTH  - PANEL_W) // 2
    PANEL_Y = (SCREEN_HEIGHT - PANEL_H) // 2 - 10
    
    COL1_X = PANEL_X + 30
    COL2_X = PANEL_X + PANEL_W // 2 + 15
    IW = 320 # Lebar standar widget
    IH = 34  # Tinggi standar widget
    HALF_W = (IW - 14) // 2
    
    ROW_SPACING = 52  
    Y_START = PANEL_Y + 65

    # --- 2. Inisialisasi Komponen UI (Murni Fokus ke Hide & Seek) ---
    # Baris 1: Grid (Kiri) & Amnesti AI (Kanan)
    rows_input = IntInputBox(COL1_X, Y_START, HALF_W, IH, "ROWS", default=10)
    cols_input = IntInputBox(COL1_X + HALF_W + 14, Y_START, HALF_W, IH, "COLUMNS", default=10)
    
    forgiveness_dd = Dropdown(COL2_X, Y_START, IW, IH, "AGENT FORGIVENESS",
                              ["Never Forgives", "Holds Grudges", "Moderate", "Quickly Forgets"][::-1])

    # Baris 2: Timer + Probabilitas dinding + Propagasi tembus dinding
    timer_input = IntInputBox(COL1_X, Y_START + 4 + ROW_SPACING, HALF_W, IH, "TIMER (SECONDS)", default=300)
    wall_prob_input = FloatInputBox(
        COL1_X + HALF_W + 14, Y_START + ROW_SPACING + 4, HALF_W, IH, "WALL PROBABILITY", default=0.5
    )
    
    wall_noise_dd = Dropdown(COL2_X, Y_START + ROW_SPACING + 4, IW, IH, "WALL PROPAGATION (PROB & NOISE)",
                             ["Completely Blocked", "Strongly Reduced", "Partially Reduced", "Easily Pass Through"])

    # Baris 3: Penglihatan Player naik ke baris 3 (Kiri) & Keamanan Hiding Cell (Kanan)
    player_vision_dd = Dropdown(COL1_X, Y_START + ROW_SPACING * 2 + 8, IW, IH, "PLAYER'S VISION",
                                 ["Short", "Normal", "Far", "Very Far"])
    
    hiding_safety_dd = Dropdown(COL2_X, Y_START + ROW_SPACING * 2 + 8, IW, IH, "HIDING CELL SAFETY",
                                ["Never Get Checked", "Mostly Being Ignored", "Usually Not Considered", "Feeling Suspicious"])

    # Baris 4: Penglihatan Agent naik ke baris 3 (Kiri), sisi kanan berlanjut dengan gap
    agent_vision_dd = Dropdown(COL1_X, Y_START + ROW_SPACING * 3 + 12, IW, IH, "AGENT'S VISION",
                                ["Short", "Normal", "Far", "Very Far"])
    
    noise_sens_dd = Dropdown(COL2_X, Y_START + ROW_SPACING * 3 + 12, IW, IH, "AGENT'S SENSITIVITY TO NOISE",
                             ["Low", "Moderate", "High", "Very High"])

    # Baris 5: Sisi kanan paling bawah dengan gap
    agent_mem_dd = Dropdown(COL2_X, Y_START + ROW_SPACING * 4 + 16, IW, IH, "AGENT'S MEMORY CAPACITY",
                            ["Low", "Medium", "High", "Very High"])

    # Tombol Menu Kontrol Utama
    start_btn = NeonButton(SCREEN_WIDTH // 2 - 185, PANEL_Y + PANEL_H - 35, "> START GAME",
                           NEON_GREEN, DIM_GREEN)
    back_btn  = NeonButton(SCREEN_WIDTH // 2 + 160, PANEL_Y + PANEL_H - 35, "> BACK",
                           NEON_PURPLE, (65, 0, 95))

    # --- 3. Dictionary Mappings Nilai Numerik Internal (Sesuai play_menu.md) ---
    MAP_FORGIVENESS = {"Never Forgives": 0., "Holds Grudges": 0.075, "Moderate": 0.125, "Quickly Forgets": 0.175}
    MAP_WALL_NOISE  = {"Completely Blocked": float("inf"), "Strongly Reduced": 3, "Partially Reduced": 2, "Easily Pass Through": 1}
    MAP_HIDING      = {"Never Get Checked": 1., "Mostly Being Ignored": 0.66, "Usually Not Considered": 0.33, "Feeling Suspicious": 0.}
    MAP_SENSITIVITY = {"Low": 3, "Moderate": 5, "High": 7, "Very High": 9}
    MAP_P_VISION    = {"Short": 3, "Normal": 4, "Far": 5, "Very Far": 6}
    MAP_A_VISION    = {"Short": 4, "Normal": 6, "Far": 8, "Very Far": 10}
    MAP_A_MEMORY    = {"Low": 30, "Medium": 50, "High": 70, "Very High": 90}

    t           = start_t
    blurred_bg  = None
    last_bg_t   = -999.0
    BG_REFRESH  = 2.0

    running = True
    state_dict = {}

    while running:
        dt = clock.tick(FPS) / 1000.0
        t += dt
        mouse_pos = pygame.mouse.get_pos()

        # Daftar seluruh dropdown aktif untuk mendeteksi event klik mouse
        all_dropdowns = [
            forgiveness_dd, wall_noise_dd, hiding_safety_dd, 
            player_vision_dd, noise_sens_dd, agent_vision_dd, agent_mem_dd
        ]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # KONDISI: KLIK BACK -> Kembali ke Main Menu Utama
                if back_btn.is_clicked(mouse_pos) and not agent_mem_dd.open:
                    state_dict = {
                        "state": 0,
                        "game_dict": None,
                        "player_dict": None,
                        "agent_dict": None,
                    }
                    running = False
                    break
                
                # KONDISI: KLIK START GAME -> Melakukan enkapsulasi data ke state_dict
                elif start_btn.is_clicked(mouse_pos):
                    rows = rows_input.value
                    cols = cols_input.value
                    timer = timer_input.value
                    wall_prob = wall_prob_input.value
                    
                    # Validasi batas minimal ukuran grid labirin (minimal 10)
                    if rows and rows < 10: rows_input.error = True; rows = None
                    if cols and cols < 10: cols_input.error = True; cols = None
                    if timer < 60: timer_input.error = True; timer = None
                    if not (0 <= wall_prob <= 1.): wall_prob_input.error = True; wall_prob = None

                    if rows and cols and timer and wall_prob:
                        # ─── OPSIONAL: POTONGAN KODE BYPASS TESTING MANDIRI ───
                        # Jika ingin langsung memulai game tanpa file manager dari temanmu,
                        # kamu bisa un-comment baris di bawah ini untuk testing!
                        """
                        from ..generation.generate_all import generate
                        from .gameplay import game_screen
                        start_pos, goal_pos, maze_data = generate(rows, cols, 0.3)
                        running = False
                        game_screen(maze_data, rows, cols, "DFS", None, 0.3, start_pos, goal_pos, t)
                        break
                        """
                        # ──────────────────────────────────────────────────────

                        # Bentuk data state_dict numerik final sesuai instruksi tugas kelompok
                        state_dict = {
                            "state": 3,
                            "game_dict": {
                                "row_size": rows,
                                "col_size": cols,
                                "timer": timer,
                                "wall_prob": wall_prob,
                                "prob_decay": MAP_FORGIVENESS[forgiveness_dd.value],
                                "wall_reduction": MAP_WALL_NOISE[wall_noise_dd.value],
                                "hiding_cell_reduction": MAP_HIDING[hiding_safety_dd.value],
                                "range_raise_prob": MAP_SENSITIVITY[noise_sens_dd.value],
                                "max_mem": MAP_A_MEMORY[agent_mem_dd.value]
                            },
                            "player_dict": {
                                "vision_range": MAP_P_VISION[player_vision_dd.value],
                            }, 
                            "agent_dict": {
                                "vision_range": MAP_A_VISION[agent_vision_dd.value],
                            }
                        }
                        running = False
                        break
                    else:
                        if not rows_input.value: rows_input.error = True
                        if not cols_input.value: cols_input.error = True
                        if not timer_input.value: timer_input.error = True
                        if not wall_prob_input.value: wall_prob_input.error = True

            # Mengatur fokus klik mouse agar dropdown tidak tembus ke widget belakang
            any_open = any(dd.open for dd in all_dropdowns)
            consumed = False
            for dd in all_dropdowns:
                if dd.handle_event(event, mouse_pos):
                    for other in all_dropdowns:
                        if other != dd: other.close()
                    consumed = True
                    break
            
            if not consumed and not any_open:
                rows_input.handle_event(event, mouse_pos)
                cols_input.handle_event(event, mouse_pos)
                timer_input.handle_event(event, mouse_pos)
                wall_prob_input.handle_event(event, mouse_pos)

        # Update hover status mouse dan animasi glow
        for dd in all_dropdowns:
            dd.update(mouse_pos)

        rows_input.update(dt)
        cols_input.update(dt)
        timer_input.update(dt)
        wall_prob_input.update(dt)
        start_btn.update(mouse_pos, dt)
        back_btn.update(mouse_pos, dt)

        # --- 4. Proses Rendering Komponen Grafis Neon ---
        if blurred_bg is None or (t - last_bg_t) > BG_REFRESH:
            blurred_bg = build_blurred_bg(t)
            last_bg_t  = t

        screen.blit(blurred_bg, (0, 0))
        dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 70))
        screen.blit(dim, (0, 0))

        draw_corner_decorations(screen, t)

        # Menggambar Kotak Frame Window Utama
        panel_bg = pygame.Surface((PANEL_W, PANEL_H), pygame.SRCALPHA)
        panel_bg.fill((0, 16, 14, 225)) 
        pygame.draw.rect(panel_bg, (*NEON_CYAN, 55), panel_bg.get_rect(), 2, border_radius=10)
        screen.blit(panel_bg, (PANEL_X, PANEL_Y))

        title_s = font_sub.render("GAME CONFIGURATION", True, NEON_CYAN)
        screen.blit(title_s, title_s.get_rect(centerx=SCREEN_WIDTH // 2, y=PANEL_Y + 14))
        
        sep_y = PANEL_Y + 42
        sep_s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(sep_s, (*NEON_CYAN, 60), (PANEL_X + 16, sep_y), (PANEL_X + PANEL_W - 16, sep_y), 1)
        screen.blit(sep_s, (0, 0))

        # Render static input boxes
        rows_input.draw(screen)
        cols_input.draw(screen)
        timer_input.draw(screen)
        wall_prob_input.draw(screen)

        # Menggunakan urutan sorting Y terbesar-ke-terkecil (Bottom-to-Top) 
        # Biar isi list dropdown atas aman berada di depan (tidak tertimpa box bawahnya)
        all_dropdowns.sort(key=lambda dd: dd.rect.y, reverse=True)
        for dd in all_dropdowns:
            dd.draw(screen)

        start_btn.draw(screen)
        if not agent_mem_dd.open:
            back_btn.draw(screen)

        screen.blit(SCANLINE_SURF, (0, 0))
        pygame.display.flip()

    return state_dict