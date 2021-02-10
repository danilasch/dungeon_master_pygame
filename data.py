import pygame
import os
import sys
from settings import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def change_cursor(cursor_image):
    cursor_image = pygame.image.load(cursor_image).convert_alpha()

    pygame.mouse.set_visible(False)

    return cursor_image


def load_image(name):
    fullname = os.path.join('data', 'pics', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def sound(name, volume=1):
    fullname = os.path.join('data', 'sounds', name)
    result = pygame.mixer.Sound(fullname)
    result.set_volume(volume)

    return result


# sounds
button_sound = sound('button.wav', 0.5)
background_music = sound('background.wav', 0.1)
door_open = sound('door_open.wav', 1)
door_close = sound('door_close.wav', 1)

# pics
inactive_btn = load_image('inactive_button.png')
active_btn = load_image('active_button.png')
inactive_box = load_image('inactive_checkbox.png')
active_box = load_image('active_checkbox.png')
background = pygame.transform.scale(load_image('background.jpg'), (WIDTH, HEIGHT))
main_cursor = os.path.join('data', 'pics', 'cursor.png')

# fonts
main_font = os.path.join('data', 'fonts', 'main_font.ttf')
head_font = os.path.join('data', 'fonts', 'head_font.ttf')

# tiles
TILE_WIDTH = TILE_HEIGHT = 50
tile_images = {
    'floor': load_image('floor.png'), 'wall': load_image('wall.png'),
    'parquet': load_image('parquet.png'), 'sport': load_image('sport_parquet.png'),
    'entry_h': load_image('entry_h.png'), 'exit_h': load_image('exit_h.png'),
    'exit_v': load_image('exit_v.png'), 'empty': load_image('empty.png')
}

wall_images = {
    'class1': load_image('classboard_fl.png'), 'class2': load_image('classboard_math.png'),
    'class3': load_image('classboard_russia.png'), 'class4': load_image('classboard_eurika.png'),
    'classwall': load_image('classwall.png'), 'entry_v0': load_image('entry_v0.png'),
    'entry_v1': load_image('entry_v1.png'), 'entry_v2': load_image('entry_v2.png'),
    'parquet': load_image('long_parquet.png')
}

interface_images = {
    'health': load_image('health.png'), 'defence': load_image('shield.png'),
    'mana': load_image('mana.png')
}
