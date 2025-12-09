import pygame as pg

# load all the backgrounds, banners, guns, target sprites (animations)

def load_assets():

    backgrounds = []
    banners = []
    guns = []
    goals_images = [[], [], []]

    for i in range(1, 4):
        # Convert to display format for speed; keep alpha for banners/guns
        backgrounds.append(pg.image.load(f"backgrounds/{i}.png").convert())
        banners.append(pg.image.load(f"banners/{i}.png").convert_alpha())
        guns.append(pg.transform.scale(pg.image.load(f"guns/{i}.png").convert_alpha(),(100, 100)))
        if i < 3:
            for j in range(1, 4):
                goals_images[i - 1].append(pg.transform.scale(pg.image.load(f"targets/{i}/{j}.png").convert_alpha(),(130 - (j*20), 80 - (j*10))))
        else:

            for j in range(1, 5):
                goals_images[i - 1].append(pg.transform.scale(
                    pg.image.load(f"targets/{i}/{j}.png").convert_alpha(),(130 - (j*20), 80 - (j*10))))
    return backgrounds, banners, guns, goals_images

def high_score():
    """read the high scores in the same order thye are written
    line 1: best_freeplay
    line 2: best_ammo
    line 3: best timed
    
    returning (best_freeplay, best_ammo, best_timed). 
    if the file is missing or invalid, default to zeroos
    only digits are in the file
    """
    
    file = open('high_scores.txt', 'r')
    lines = file.readlines()

    while len(lines) < 3:
        lines.append("0")
    best_freeplay = int(lines[0].strip())
    best_ammo = int(lines[1].strip())
    best_timed = int(lines[2].strip())
    return best_freeplay, best_ammo, best_timed
