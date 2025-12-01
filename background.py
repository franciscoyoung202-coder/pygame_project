import pygame as pg
from configuration import *

pg.init()

brown = (150, 75, 0)
light_brown = (196, 164, 132)

font = pg.font.Font(game_font, 90)
big_font = pg.font.Font(game_font, 54)

# goose image
goose_raw = pg.image.load("menus/goose.png")
scaled_goose = pg.transform.scale(goose_raw, (200, 150))

# text
txt_goose = font.render("GOOSE", True, brown)
txt_hunt = font.render("HUNT",  True, brown)
txt_game = font.render("GAME", True, brown)
txt_paused = font.render("PAUSED", True, brown)
txt_over = big_font.render("OVER", True, brown)


def draw_menu_background(screen):

    screen.fill((0, 0, 0))

    txt_goose_rect = txt_goose.get_rect(center=(window_width // 2 - 50,
                                                window_height // 2 - 225))
    screen.blit(txt_goose, txt_goose_rect)

    txt_hunt_rect = txt_hunt.get_rect(center=(window_width // 2 + 40,
                                              window_height // 2 - 100))
    screen.blit(txt_hunt, txt_hunt_rect)

    goose_img_rect = scaled_goose.get_rect()
    goose_img_rect.midright = (txt_hunt_rect.left - 20, txt_hunt_rect.centery)
    screen.blit(scaled_goose, goose_img_rect)

    pg.draw.rect(
        screen,
        light_brown,
        (txt_goose_rect.left, txt_goose_rect.bottom + 15,
         txt_goose_rect.width + 75, 8)
    )

def draw_pause_background(screen):
    """
    Draw the pause background and buttons with hover-enlarge visual.
    Returns: resume_button, menu_button (logical rects for click testing).
    """
    screen.fill((0, 0, 0))

    txt_game_rect = txt_game.get_rect(center=(window_width // 2 - 50,
                                              window_height // 2 - 225))
    screen.blit(txt_game, txt_game_rect)

    txt_paused_rect = txt_paused.get_rect(center=(window_width // 2 + 40,
                                                  window_height // 2 - 100))
    screen.blit(txt_paused, txt_paused_rect)

    goose_img_rect = scaled_goose.get_rect()
    goose_img_rect.midright = (txt_paused_rect.left - 20, txt_paused_rect.centery)
    screen.blit(scaled_goose, goose_img_rect)

    pg.draw.rect(
        screen,
        light_brown,
        (txt_game_rect.left, txt_game_rect.bottom + 15,
         txt_game_rect.width + 75, 8)
    )

    dark_color = (145, 121, 77)
    light_color = (200, 173, 127)

    resume_button = pg.Rect((80, 450), (260, 100))
    menu_button = pg.Rect((540, 450), (260, 100))

    font_main = pg.font.Font(game_font, 30)
    font_small = pg.font.Font(game_font, 22)

    buttons = [
        (resume_button, "RESUME", ""),
        (menu_button, "MAIN", "MENU"),
    ]

    mouse_pos = pg.mouse.get_pos()

    for rect, label, lwlabel in buttons:
        # enlarge
        if rect.collidepoint(mouse_pos):
            enlarge = 1.10
            new_width = int(rect.width * enlarge)
            new_height = int(rect.height * enlarge)
            draw_rect = pg.Rect(0, 0, new_width, new_height)
            draw_rect.center = rect.center
        else:
            draw_rect = rect

        pg.draw.rect(screen, light_color, draw_rect)
        pg.draw.rect(screen, dark_color, draw_rect, 4)

        txt = font_main.render(label, True, dark_color)
        txt_rect = txt.get_rect(center=(draw_rect.centerx + 2, draw_rect.centery - 12))
        screen.blit(txt, txt_rect)

        if lwlabel:
            sub_txt = font_small.render(lwlabel, True, dark_color)
            sub_rect = sub_txt.get_rect(center=(draw_rect.centerx, draw_rect.centery + 26))
            screen.blit(sub_txt, sub_rect)


    return resume_button, menu_button


def draw_exit_background(screen, mode, mode_freeplay, points, time_elapsed):
    """
    Draw the exit background and buttons with enlarge visual.
    Returns: resume_button, menu_button (logical rects for click testing).
    """
    screen.fill((0, 0, 0))
    # Game txt
    txt_game_rect = txt_game.get_rect(center=(window_width // 2 - 50,
                                              window_height // 2 - 225))
    screen.blit(txt_game, txt_game_rect)
    # over txt
    txt_over_rect = txt_over.get_rect(center=(window_width // 2 + 40,
                                                  window_height // 2 - 100))
    screen.blit(txt_over, txt_over_rect)

    goose_img_rect = scaled_goose.get_rect()
    goose_img_rect.midright = (txt_over_rect.left - 20, txt_over_rect.centery)
    screen.blit(scaled_goose, goose_img_rect)

    pg.draw.rect(
        screen,
        light_brown,
        (txt_game_rect.left, txt_game_rect.bottom + 15,
         txt_game_rect.width + 75, 8)
    )

    dark_color = (145, 121, 77)
    light_color = (200, 173, 127)

    exit_button = pg.Rect((80, 450), (260, 100))
    menu_button = pg.Rect((540, 450), (260, 100))

    font_main = pg.font.Font(game_font, 30)
    font_small = pg.font.Font(game_font, 22)

    buttons = [
        (exit_button, "EXIT", "OUT"),
        (menu_button, "MAIN", "MENU"),
    ]

    mouse_pos = pg.mouse.get_pos()

    for rect, label, lwlabel in buttons:
        # enlarge
        if rect.collidepoint(mouse_pos):
            enlarge = 1.10
            new_width = int(rect.width * enlarge)
            new_height = int(rect.height * enlarge)
            draw_rect = pg.Rect(0, 0, new_width, new_height)
            draw_rect.center = rect.center
        else:
            draw_rect = rect

        pg.draw.rect(screen, light_color, draw_rect)
        pg.draw.rect(screen, dark_color, draw_rect, 4)

        txt = font_main.render(label, True, dark_color)
        txt_rect = txt.get_rect(center=(draw_rect.centerx + 2, draw_rect.centery - 12))
        screen.blit(txt, txt_rect)

        if lwlabel:
            sub_txt = font_small.render(lwlabel, True, dark_color)
            sub_rect = sub_txt.get_rect(center=(draw_rect.centerx, draw_rect.centery + 26))
            screen.blit(sub_txt, sub_rect)

    if mode == mode_freeplay:
        display_score = time_elapsed
        score_surf = big_font.render(f"HIGH SCORE: {display_score}s", True, light_color)
        score_rect = score_surf.get_rect(center=(window_width // 2, 350))
        screen.blit(score_surf, score_rect)
    else:
        display_score = points
        # Render the score in black and center it near the top
        score_surf = big_font.render(f"HIGH SCORE: {display_score} pts", True, light_color)
        score_rect = score_surf.get_rect(center=(window_width // 2, 350))
        screen.blit(score_surf, score_rect)



    return exit_button, menu_button