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
    """

    mouse_x, mouse_y = pg.mouse.get_pos()
    gun_point = ((window_width + 120) // 2, window_height - 125)
    lasers = ['red', 'purple', 'green']
    clicks = pg.mouse.get_pressed()

    dx = mouse_x - gun_point[0]
    dy = mouse_y - gun_point[1]
    # to fix divide by 0
    if dx != 0:
        slope = dy / dx
        angle = math.atan(slope)
    else:
        if dy < 0:
            angle = math.pi / 2
        else:
            angle = -math.pi / 2

    rotation = math.degrees(angle)

    # Flip gun if aiming to the left
    if mouse_x < window_width / 2:
        gun = pg.transform.flip(guns[level - 1], True, False)
        if mouse_y < window_height - 200:
            screen.blit(pg.transform.rotate(gun, 90 - rotation), (gun_point[0] - 50, gun_point[1] - 50))
            if clicks[0]:
                pg.draw.circle(screen, lasers[level - 1], (mouse_x, mouse_y), 5)
    else:
        gun = guns[level - 1]
        if mouse_y < window_height - 200:
            screen.blit(pg.transform.rotate(gun, 270 - rotation), (gun_point[0] - 50, gun_point[1] - 50))
            if clicks[0]:
                pg.draw.circle(screen, lasers[level - 1], (mouse_x, mouse_y), 5)


def check_shot(targets, coords, points):
    """
    Remove hit targets when the mouse position collides with them.
    Returns updated coords and points.
    """
    mouse_position = pg.mouse.get_pos()
    for i in range(len(targets)):
        # iterating backwards to safely remove by index
        for j in range(len(targets[i]) - 1, -1, -1):
            if targets[i][j].collidepoint(mouse_position):
                coords[i].pop(j)
                # points scaling: tiers based on index
                points += 10 + 10 * (i ** 2)

    return coords, points


def draw_score(screen, smol_font, points, total_shots, time_elapsed, mode, ammo, time_remaining):
    """
    Render and blit the current score & mode info.
    """
    y_base = 550
    line_height = 16

    def blit_line(text, line):
        surf = smol_font.render(text, True, (0, 0, 0))
        screen.blit(surf, (375, y_base + line * line_height))

    blit_line(f"Points: {points}", 0)
    blit_line(f"Total Shots: {total_shots}", 1)
    blit_line(f"Time Elapsed: {time_elapsed}s", 2)

    if mode == mode_freeplay:
        blit_line("Mode: Freeplay", 3)
    elif mode == mode_accuracy:
        blit_line(f"Mode: Accuracy | Ammo Left: {ammo}", 3)
    elif mode == mode_timed:
        blit_line(f"Mode: Timed | Time Left: {time_remaining}s", 3)


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
    new_coords
):
    dark_color = (145, 121, 77)
    light_color = (200, 173, 127)

    draw_menu_background(screen)

    mouse_pos = pg.mouse.get_pos()
    mouse_clicks = pg.mouse.get_pressed()

    freeplay_button = pg.Rect((80, 300), (260, 100))
    timed_button = pg.Rect((80, 450), (260, 100))
    accuracy_button = pg.Rect((540, 300), (260, 100))
    reset_button = pg.Rect((540, 450), (260, 100))

    font_main = pg.font.Font(game_font, 30)
    font_small = pg.font.Font(game_font, 22)

    buttons = [
        (freeplay_button, "Practice!", f"Best Time: {best_freeplay}"),
        (timed_button, "Timed", f"Best Score: {best_timed}"),
        (accuracy_button, "Accuracy", f"Best Score: {best_ammo}"),
        (reset_button, "Reset Scores", "Clear SCORES"),
    ]

    for rect, label, best_label in buttons:
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

        txt = font_main.render(label, True, dark_color)
        txt_rect = txt.get_rect(center=(draw_rect.centerx + 2, draw_rect.centery - 12))
        screen.blit(txt, txt_rect)

        best_txt = font_small.render(best_label, True, dark_color)
        best_rect = best_txt.get_rect(center=(draw_rect.centerx, draw_rect.centery + 26))
        screen.blit(best_txt, best_rect)

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
        new_coords
    )

def draw_game_over(screen, mode, time_elapsed, points, big_font, clicked,
                   level, pause, game_over, menu, total_shots, time_remaining,
                     running, mode_freeplay):
    """
    Draw the game over screen and handle exit/menu clicks.
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
    if exit_button.collidepoint(mouse_pos) and mouse_clicks[0] and not clicked:
        running = False
        sys.exit(0)

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