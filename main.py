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
smol_font = pg.font.Font(game_font, 15)  # smaller HUD font
smol_font_back = pg.font.Font(game_font, 8)
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

# music
pg.mixer.init()

pg.mixer.music.load('sounds/intro_music.mp3') # in the main menu
pg.mixer.music.play(-1)

quack_sound = pg.mixer.Sound("sounds/duck-quack-112941.mp3")
quack_sound.set_volume(.15)

bird_sound = pg.mixer.Sound("sounds/hit-soundvideo-game-type-230510.mp3")
bird_sound.set_volume(.15)

gun_sound = pg.mixer.Sound("sounds/gunshot-352466.mp3")
gun_sound.set_volume(0.35)



# flags
shots = False
menu = True
game_over = False
pause = False
clicked = False
write_values = False
new_coords = True  # when True, rebuild enemies
instructions_open = False  # menu overlay


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
    if level > 0:
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
            new_coords,
            instructions_open
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
            new_coords,
            instructions_open
        )
        # If we just left the menu to start a game, rebuild enemies
        if not menu and level > 0:
            new_coords = True
            # optional: change to in-game music if you have one
            try:
                pg.mixer.music.load('sounds/game_music.mp3')
                pg.mixer.music.play(-1)
            except Exception:
                pass

    if game_over:
        level = 0
        # CAPTURE returned state so clicks persist
        (
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
        ) = draw_game_over(
            screen, mode, time_elapsed, points, big_font, clicked,
            level, pause, game_over, menu, total_shots, time_remaining, running, mode_freeplay
        )

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

    # Ensure goal_boxes exists before checks later
    goal_boxes = [[], [], []]

    # Level handling: draw, move, shots
    if not pause:
        if level == 1:
            goal_boxes = draw_level(screen, goals_images, level, one_coords)
            one_coords = move_level(one_coords, window_width)
            if shots:
                one_coords, points = check_shot(goal_boxes, one_coords, points, bird_sound, quack_sound, gun_sound, level)
                shots = False
        elif level == 2:
            goal_boxes = draw_level(screen, goals_images, level, two_coords)
            two_coords = move_level(two_coords, window_width)
            if shots:
                two_coords, points = check_shot(goal_boxes, two_coords, points, bird_sound, quack_sound, gun_sound, level)
                shots = False
        elif level == 3:
            goal_boxes = draw_level(screen, goals_images, level, three_coords)
            three_coords = move_level(three_coords, window_width)
            if shots:
                three_coords, points = check_shot(goal_boxes, three_coords, points, bird_sound, quack_sound, gun_sound, level)
                shots = False

    # hud + gun
    # Hide HUD on pause or game over
    if level > 0 and not pause and not game_over:
        draw_gun(screen, guns, level, window_width, window_height)
        draw_score(screen, smol_font_back, points, total_shots, time_elapsed, mode, ammo, time_remaining)

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
                pg.mixer.music.load('sounds/intro_music.mp3')
                pg.mixer.music.play(-1)
                clicked = False
                new_coords = True
                instructions_open = False  # ensure overlay is closed when returning to menu

    # Level progression: advance if all targets are gone
    if level > 0 and not pause:
        if goal_boxes == [[], [], []] and level < 3:
            level += 1
            new_coords = True
        if level == 3 and goal_boxes == [[],[],[],[]] or (mode == 1 and ammo == 0) or (mode == 2 and time_remaining == 0):
            new_coords = True
            pg.mixer.music.load('sounds/intro_music.mp3')
            pg.mixer.music.play(-1)
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
        write_values = False
        
    # updates everything
    pg.display.flip()