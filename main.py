import pygame as pg
import sys

from configuration import *
from game_mechanics import ( # only the functions because
    draw_gun,
    check_shot,
    draw_score,
    draw_menu,
    draw_game_over,
    draw_pause,
    mode_freeplay,
    mode_accuracy,
    mode_timed,
)

from levels import *
from assets import *
from assets import high_score


pg.init()

# timer and font
timer = pg.time.Clock()
smol_font = pg.font.Font(game_font, 20)
big_font = pg.font.Font(game_font, 54)


# screen
screen = pg.display.set_mode([window_width, window_height])


# assets
backgrounds, banners, guns, goals_images = load_assets()

# points and game state
points = 0
total_shots = 0
mode = mode_accuracy
ammo = 5  # placeholder
time_elapsed = 0
time_remaining = 0
counter = 1
level = 0
resume_level = 0

# best scores
best_freeplay = 0
best_ammo = 0
best_timed = 0

# overwrite high scores on high_score.txt
best_freeplay, best_ammo, best_timed = high_score()

# flags
shots = False
menu = True
game_over = False
pause = False
clicked = False
write_values = False
new_coords = True  # when True, rebuild enemies

# load images
menu_img = pg.image.load(f"menus/mainMenu.png")
pause_img = pg.image.load(f'menus/pause.png')
game_over_img = pg.image.load('menus/gameOver.png')

# coordinates of enemies 'goals'
one_coords, two_coords, three_coords = build_coords(goals, window_width)

running = True
while running:

    clock = timer.tick(fps)


    # timer / mode
    if level != 0 and not pause:
        if counter < 60:
            counter += 1
        else:
            counter = 1
            time_elapsed += 1
            if mode == mode_timed and time_remaining > 0:
                time_remaining -= 1


    # Draw order: clear -> background -> banner
    screen.fill((0,0,0))
    screen.blit(backgrounds[level - 1], (0, 0))
    screen.blit(banners[level - 1], (0, 10))

    if menu:
        level = 0
        (
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
        ) = draw_menu(
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
        )
        # If we just left the menu to start a game, rebuild enemies
        if not menu and level > 0:
            new_coords = True

    if game_over:
        level = 0
        draw_game_over(screen, mode, time_elapsed, points, big_font, clicked,
                   level, pause, game_over, menu, total_shots, time_remaining, running, mode_freeplay)
    if pause:
        if pause:
            (
            level,
            pause,
            menu,
            points,
            total_shots,
            time_elapsed,
            time_remaining,
            clicked,
            new_coords,
        ) = draw_pause(
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
        )
    # Rebuild enemies when requested
    if new_coords:
        one_coords, two_coords, three_coords = build_coords(goals, window_width)
        new_coords = False


    # Level handling: draw, move, shots
    if not pause:
        if level == 1:
            goal_boxes = draw_level(screen, goals_images, level, one_coords)
            one_coords = move_level(one_coords, window_width)
            if shots:
                one_coords, points = check_shot(goal_boxes, one_coords, points)
                shots = False
        elif level == 2:
            goal_boxes = draw_level(screen, goals_images, level, two_coords)
            two_coords = move_level(two_coords, window_width)
            if shots:
                two_coords, points = check_shot(goal_boxes, two_coords, points)
                shots = False
        elif level == 3:
            goal_boxes = draw_level(screen, goals_images, level, three_coords)
            three_coords = move_level(three_coords, window_width)
            if shots:
                three_coords, points = check_shot(goal_boxes, three_coords, points)
                shots = False

    # hud + gun
    if level > 0:
        draw_gun(screen, guns, level, window_width, window_height)
        draw_score(screen, smol_font, points, total_shots, time_elapsed, mode, ammo, time_remaining)

    # Events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            pg.quit()
            sys.exit(0)

        # Reset clicked when the mouse button is released so pause/menu can be clicked again
        if event.type == pg.MOUSEBUTTONUP and event.button == 1:
            clicked = False

        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_position = pg.mouse.get_pos()
            # Ignore shooting and in-game clicks while paused (pause menu handles its own clicks)
            if not pause:
                # Prevent shooting inside the banner area (bottom area excluded)
                if (0 < mouse_position[0] < window_width) and (0 < mouse_position[1] < window_height - 200):
                    if mode == mode_accuracy and ammo <= 0:
                        pass
                    else:
                        shots = True
                        total_shots += 1
                        if mode == mode_accuracy:
                            ammo -= 1  # Count down remaining ammo
             # pause button area
            if (602 < mouse_position[0] < 712) and (530 < mouse_position[1] < 582) and not clicked and level > 0:
                resume_level = level
                pause = True
                clicked = True

            # reset-to-menu area
            if (602 < mouse_position[0] < 712) and (593 < mouse_position[1] < 644) and not pause:
                menu = True
                clicked = False
                new_coords = True

    # Level progression: advance if all targets are gone
    if level > 0 and not pause:
        if goal_boxes == [[], [], []] and level < 3:
            level += 1
        if level == 3 and goal_boxes == [[],[],[],[]] or (mode == 1 and ammo == 0) or (mode == 2 and time_remaining == 0):
            new_coords = True
            if mode == 0:
                if time_elapsed < best_freeplay or best_freeplay == 0:
                    best_freeplay = time_elapsed
                    write_values = True
            if mode == 1:
                if points > best_ammo:
                    best_ammo = points
                    write_values = True
            if mode == 2:
                if points > best_timed:
                    best_timed = points
                    write_values = True
            game_over = True
            
    if write_values:
        file = open('high_scores.txt', 'w')
        file.write(f'{best_freeplay}\n{best_ammo}\n{best_timed}')
        file.close()
        write_values = False
        
    # updates everything
    pg.display.flip()