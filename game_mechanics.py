import pygame as pg
import sys
import math
from configuration import *
from background import draw_menu_background, draw_pause_background, draw_exit_background

# Mode constants for clarity
mode_freeplay = 0
mode_accuracy = 1
mode_timed = 2

def draw_gun(screen, guns, level, window_width, window_height):
    """
    Draw the gun pointing toward the mouse. Fires a colored dot when the left mouse button is held.

    Minimal fix:
    - Decide flip using the gun pivot (gun_point.x), not the window center.
    - When aiming straight up (dx == 0), always use the LEFT branch so 90 - 90 = 0 (no 180° flip).
    """

    mouse_x, mouse_y = pg.mouse.get_pos()
    gun_point = ((window_width + 120) // 2, window_height - 125)
    lasers = [(255, 0, 0), (128, 0, 128), (0, 128, 0)]
    clicks = pg.mouse.get_pressed()

    dx = mouse_x - gun_point[0]
    dy = mouse_y - gun_point[1]

    # Original angle-from-slope logic
    if dx != 0:
        slope = dy / dx
        angle = math.atan(slope)
    else:
        if dy < 0:
            angle = math.pi / 2
        else:
            angle = -math.pi / 2

    rotation = math.degrees(angle)

    # Safe indexing for the game
    gun_idx = max(0, min(level - 1, len(guns) - 1))
    laser_idx = max(0, min(level - 1, len(lasers) - 1))

    # fix 1: Use the pivot x coord (gun_point[0]) to choose side, not window_width/2
    # fix 2: for dx == 0 (straight up), make it so that the left side to avoid 180 degrees flip when aiming straight up
    use_left_branch = dx <= 0  # left if mouse is at or left of pivot; right only if dx > 0

    if use_left_branch:
        gun = pg.transform.flip(guns[gun_idx], True, False)
        if mouse_y < window_height - 200:
            # For straight up (rotation == 90), this yields 0°, avoiding the 180° jump
            screen.blit(pg.transform.rotate(gun, 90 - rotation), (gun_point[0] - 50, gun_point[1] - 50))
            if clicks[0]:
                pg.draw.circle(screen, lasers[laser_idx], (mouse_x, mouse_y), 5)
    else:
        gun = guns[gun_idx]
        if mouse_y < window_height - 200:
            screen.blit(pg.transform.rotate(gun, 270 - rotation), (gun_point[0] - 50, gun_point[1] - 50))
            if clicks[0]:
                pg.draw.circle(screen, lasers[laser_idx], (mouse_x, mouse_y), 5)


def check_shot(targets, coords, points, bird_sound, quack_sound, gun_sound, level):
    """
    Remove hit targets when the mouse position collides with them.
    Returns updated coords and points.
    """
    mouse_position = pg.mouse.get_pos()
    for i in range(len(targets)):
        # iterating backwards to safely remove by index
        for j in range(len(targets[i]) - 1, -1, -1):
            if targets[i][j].collidepoint(mouse_position):
                if i < len(coords) and j < len(coords[i]):  # avoid out-of-range pops
                    coords[i].pop(j)
                # points scaling: tiers based on index
                points += 10 + 10 * (i ** 2)
                if level == 1:
                    bird_sound.play()
                elif level == 2:
                    quack_sound.play()
                elif level == 3:
                    gun_sound.play()
    return coords, points


def draw_score(screen, smol_font_back, points, total_shots, time_elapsed, mode, ammo, time_remaining):
    """
    Render and blit the current score & mode info with dark brown text.
    """
    y_base = 546
    line_height = 16
    x_base = 370
    dark_color = (149, 149, 77)

    def blit_line(text, line):
        surf = smol_font_back.render(text, True, dark_color)
        screen.blit(surf, (x_base, y_base + line * line_height))

    blit_line(f"Points: {points}", 0)
    blit_line(f"Total Shots: {total_shots}", 1)
    blit_line(f"Time Elapsed: {time_elapsed}s", 2)

    if mode == mode_freeplay:
        blit_line("Mode: Freeplay", 3)
    elif mode == mode_accuracy:
        blit_line(f"Ammo Left {ammo}", 3)
        blit_line(f"Mode: Accuracy", 4)
    elif mode == mode_timed:
        blit_line(f"Mode Timed", 4)
        blit_line(f"Time Left: {time_remaining}s", 3)


def draw_menu(
    screen,
    best_freeplay,
    best_ammo,
    best_timed,
    game_over,
    pause,
    mode,
    level,
    menu,
    time_elapsed,
    total_shots,
    ammo,
    points,
    clicked,
    write_values,
    time_remaining,
    new_coords,
    instructions_open
):
    dark_color = (145, 121, 77)
    light_color = (200, 173, 127)

    draw_menu_background(screen)

    mouse_pos = pg.mouse.get_pos()
    mouse_clicks = pg.mouse.get_pressed()

    # Rect buttons (your original four)
    freeplay_button = pg.Rect((80, 300), (260, 100))
    timed_button = pg.Rect((80, 450), (260, 100))
    accuracy_button = pg.Rect((540, 300), (260, 100))
    reset_button = pg.Rect((540, 450), (260, 100))

    # Text-only buttons: Instructions and Exit (no big rects, just text hitboxes)
    font_main = pg.font.Font(game_font, 23)
    font_small = pg.font.Font(game_font, 16)
    font_tiny = pg.font.Font(None, 19)  # very small font for rect

    instr_label = font_main.render("Instructions", True, dark_color)
    exit_label = pg.font.Font(game_font, 28).render("Exit", True, dark_color)

    # Move both up to avoid misclicks near the bottom edge
    instr_pos = (window_width // 2, 590)  # was 610
    exit_pos = (window_width // 2, 625)   # was 650

    instr_rect = instr_label.get_rect(center=instr_pos)
    exit_rect = exit_label.get_rect(center=exit_pos)

    # Draw rectangular buttons (original look)
    buttons = [
        (freeplay_button, "Practice", f"Best Time {best_freeplay}"),
        (timed_button, "Timed", f"Best Score {best_timed}"),
        (accuracy_button, "Accuracy", f"Best Score {best_ammo}"),
        (reset_button, "Reset Scores", "Clear SCORES"),
    ]

    for rect, label, best_label in buttons:
        # Hover enlarge on original buttons
        if rect.collidepoint(mouse_pos):
            enlarge = 1.10
            new_width = int(rect.width * enlarge)
            new_height = int(rect.height * enlarge)
            enlarged_rect = pg.Rect(0, 0, new_width, new_height)
            enlarged_rect.center = rect.center
            draw_rect = enlarged_rect
        else:
            draw_rect = rect

        pg.draw.rect(screen, light_color, draw_rect)
        pg.draw.rect(screen, dark_color, draw_rect, 4)

        # Use dark_color for text; slight x nudge avoids left border overlap
        txt = font_main.render(label, True, dark_color)
        txt_rect = txt.get_rect(center=(draw_rect.centerx + 6, draw_rect.centery - 12))
        screen.blit(txt, txt_rect)

        best_txt = font_small.render(best_label, True, dark_color)
        best_rect = best_txt.get_rect(center=(draw_rect.centerx + 6, draw_rect.centery + 26))
        screen.blit(best_txt, best_rect)

    # Draw text-only buttons (no rect background)
    screen.blit(instr_label, instr_rect)
    screen.blit(exit_label, exit_rect)

    # Disable other buttons while instructions overlay is open
    if not instructions_open:
        # Original buttons clicks
        if freeplay_button.collidepoint(mouse_pos) and mouse_clicks[0] and not clicked:
            mode = mode_freeplay
            level = 1
            menu = False
            time_elapsed = 0
            total_shots = 0
            points = 0
            clicked = True
            new_coords = True
        if accuracy_button.collidepoint(mouse_pos) and mouse_clicks[0] and not clicked:
            mode = mode_accuracy
            level = 1
            menu = False
            time_elapsed = 0
            ammo = 96
            total_shots = 0
            points = 0
            clicked = True
            new_coords = True
        if timed_button.collidepoint(mouse_pos) and mouse_clicks[0] and not clicked:
            mode = mode_timed
            level = 1
            menu = False
            time_remaining = 35
            time_elapsed = 0
            total_shots = 0
            points = 0
            clicked = True
            new_coords = True
        if reset_button.collidepoint(mouse_pos) and mouse_clicks[0] and not clicked:
            best_freeplay = 0
            best_ammo = 0
            best_timed = 0
            write_values = True
            clicked = True

        # Text-only buttons clicks use their text rects
        if instr_rect.collidepoint(mouse_pos) and mouse_clicks[0] and not clicked:
            instructions_open = True
            clicked = True
        if exit_rect.collidepoint(mouse_pos) and mouse_clicks[0] and not clicked:
            clicked = True
            pg.quit()
            sys.exit(0)

    # Instructions overlay (very small font, black)
    if instructions_open:
        panel_rect = pg.Rect(120, 140, 560, 340)
        pg.draw.rect(screen, (240, 230, 200), panel_rect)
        pg.draw.rect(screen, dark_color, panel_rect, 5)

        title_font = pg.font.Font(None, 25) 
        title = title_font.render("Instructions", True, 'black')
        screen.blit(title, (panel_rect.x + 24, panel_rect.y + 16))

        # Use tiny font to prevent going over rect
        lines = [
            " Aim with your mouse.",
            " Left click to fire.",
            " Avoid clicking inside the bottom banner area.",
            "",
            " Modes:",
            "   Freeplay: Unlimited shots, track time.",
            "   Accuracy: Limited ammo; maximize points.",
            "   Timed: Score as much as you can before time runs out.",
            "",
            " Pause: Click the pause button. Resume or return to menu.",
        ]
        y = panel_rect.y + 60
        for line in lines:
            surf = font_tiny.render(line, True, 'black')
            screen.blit(surf, (panel_rect.x + 24, y))
            y += 20  # tighter line spacing with tiny font

        # Close button (small)
        close_btn = pg.Rect(panel_rect.centerx - 80, panel_rect.bottom - 70, 160, 44)
        pg.draw.rect(screen, light_color, close_btn)
        pg.draw.rect(screen, dark_color, close_btn, 3)
        close_txt = font_small.render("Close", True, dark_color)
        c_rect = close_txt.get_rect(center=close_btn.center)
        screen.blit(close_txt, c_rect)

        # Close click within the instructions button
        if close_btn.collidepoint(mouse_pos) and mouse_clicks[0] and not clicked:
            instructions_open = False
            clicked = True

    return (
        best_freeplay,
        best_ammo,
        best_timed,
        game_over,
        pause,
        mode,
        level,
        menu,
        time_elapsed,
        total_shots,
        ammo,
        points,
        clicked,
        write_values,
        time_remaining,
        new_coords,
        instructions_open
    )

def draw_game_over(screen, mode, time_elapsed, points, big_font, clicked,
                   level, pause, game_over, menu, total_shots, time_remaining,
                   running, mode_freeplay):
    """
    Draw the game over screen and handle exit/menu clicks.
    Returns updated state so the caller can apply it.
    """
    mouse_pos = pg.mouse.get_pos()
    mouse_clicks = pg.mouse.get_pressed()

    # Draw background and buttons
    exit_button, menu_button = draw_exit_background(screen, mode, mode_freeplay, points, time_elapsed)

    # Handle button clicks
    if menu_button.collidepoint(mouse_pos) and mouse_clicks[0] and not clicked:
        clicked = True
        level = 0
        pause = False
        game_over = False
        menu = True
        points = 0
        total_shots = 0
        time_elapsed = 0
        time_remaining = 0
        # Switch back to menu music
        pg.mixer.music.load('sounds/intro_music.mp3')
        pg.mixer.music.play(-1)

    if exit_button.collidepoint(mouse_pos) and mouse_clicks[0] and not clicked:
        running = False
        sys.exit(0)

    return (
        level,
        pause,
        game_over,
        menu,
        points,
        total_shots,
        time_elapsed,
        time_remaining,
        clicked,
        running
    )

def draw_pause(
    screen,
    level,
    pause,
    resume_level,
    clicked,
    menu,
    points,
    total_shots,
    time_elapsed,
    time_remaining,
    new_coords,
):

    resume_button, menu_button = draw_pause_background(screen)

    mouse_pos = pg.mouse.get_pos()
    mouse_clicks = pg.mouse.get_pressed()

    if not mouse_clicks[0]:
        clicked = False

    if resume_button.collidepoint(mouse_pos) and mouse_clicks[0] and not clicked:
        level = resume_level
        pause = False
        clicked = True

    if menu_button.collidepoint(mouse_pos) and mouse_clicks[0] and not clicked:
        pg.mixer.music.load('sounds/intro_music.mp3')
        pg.mixer.music.play(-1)
        level = 0
        pause = False
        menu = True
        points = 0
        total_shots = 0
        time_elapsed = 0
        time_remaining = 0
        clicked = True
        new_coords = True

    return level, pause, menu, points, total_shots, time_elapsed, time_remaining, clicked, new_coords