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
    file = open('high_scores.txt', 'r')
    read_score = file.readlines()
    file.close()
    best_freeplay = int(read_score[0])
    best_ammo = int(read_score[1])
    best_timed = int(read_score[2])
    return best_ammo, best_timed, best_freeplay
