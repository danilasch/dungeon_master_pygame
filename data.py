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
        # print(f"Файл с изображением '{fullname}' не найден")
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

# pics
inactive_btn = load_image('inactive_button.png')
active_btn = load_image('active_button.png')
inactive_box = load_image('inactive_checkbox.png')
active_box = load_image('active_checkbox.png')
background = load_image('background.jpg')
main_cursor = os.path.join('data', 'pics', 'cursor.png')

# fonts
main_font = os.path.join('data', 'fonts', 'main_font.ttf')
head_font = os.path.join('data', 'fonts', 'head_font.ttf')

# tiles
TILE_WIDTH = TILE_HEIGHT = 50
tile_images = {
    'floor': load_image('floor.png'), 'wall': load_image('wall.png'),
}
