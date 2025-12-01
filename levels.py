import pygame as pg

def move_level(coords, window_width):
    max_val = len(coords)
    for i in range(max_val):
        for j in range(len(coords[i])):
            my_coords = coords[i][j]
            if my_coords[0] < -150:
                coords[i][j] = (window_width, my_coords[1])
            else:
                coords[i][j] = (my_coords[0] - 2 ** i, my_coords[1])
    return coords

def draw_level(screen, goals_images, level, coords):
    goal_rects = []
    for _ in range(len(coords)):
        goal_rects.append([])
        
    for i in range(len(coords)):
        for j in range(len(coords[i])):
            goal_rects[i].append(pg.Rect(
                (coords[i][j][0] + 20, coords[i][j][1]),
                (60 - i * 12, 60 - i * 12)
            ))
            screen.blit(goals_images[level - 1][i], coords[i][j])
    return goal_rects

def build_coords(goals, window_width):
    """
    Build initial coordinates for all levels.
    level 1: 3 rows, level 2: 3 rows, level 3: 4 rows
    """
    one_coords = [[], [], []]
    two_coords = [[], [], []]
    three_coords = [[], [], [], []]

    # level 1
    for i in range(3):
        my_list = goals[1]
        for j in range(my_list[i]):
            one_coords[i].append(
                (window_width // (my_list[i]) * j,
                 300 - (i * 100) + 30 * (j % 2))
            )

    # level 2
    for i in range(3):
        my_list = goals[2]
        for j in range(my_list[i]):
            two_coords[i].append(
                (window_width // (my_list[i]) * j,
                 300 - (i * 150) + 30 * (j % 2))
            )

    # level 3 (4 rows)
    for i in range(len(goals[3])):
        my_list = goals[3]
        for j in range(my_list[i]):
            three_coords[i].append(
                (window_width // (my_list[i]) * j,
                 300 - (i * 100) + 30 * (j % 2))
            )
    return one_coords, two_coords, three_coords