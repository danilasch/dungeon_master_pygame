import pygame
import sys
import sys
import math
from settings import *
from menu import *
from data import *


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)


class Map:
    def __init__(self):
        pass

    def render(self, screen):
        pass


class Hero:
    def __init__(self, position):
        self.x, self.y = position
        self.speed = 5

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), self.get_position(), 15)


class Game:  # служебный класс игры
    def __init__(self, game_map, hero):
        self.map = game_map
        self.hero = hero
        self.dx, self.dy = 0, 0

    def render(self, screen):
        self.map.render(screen)
        self.hero.render(screen)

    def move_hero(self):
        x, y = self.hero.get_position()
        x += self.dx
        y += self.dy
        self.hero.set_position((x, y))


def change_cursor(cursor_image):
    cursor_image = pygame.image.load(cursor_image).convert_alpha()

    pygame.mouse.set_visible(False)

    return cursor_image


def get_length(vector):  # вычисление длины вектора
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2)


# вычисление длины и количества шагов, необходимых герою
# для того чтобы добраться до курсора
def calculate_motion(start_pos, final_pos, speed):
    x1, y1, = start_pos
    x2, y2 = final_pos
    vector = (x2 - x1, y2 - y1)
    length = get_length(vector)
    return speed * vector[0] / length, \
        speed * vector[1] / length, length / speed


def main():
    background_music.set_volume(0)

    hero = Hero((10, 10))
    game_map = Map()
    game = Game(game_map, hero)
    running = True
    steps, distance = 0, 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pos() != game.hero.get_position():
                    game.dx, game.dy, distance = calculate_motion(
                        game.hero.get_position(), pygame.mouse.get_pos(), game.hero.speed)
                    steps = 0

            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill(pygame.Color('black'))
        game.render(screen)

        if pygame.mouse.get_pos() != game.hero.get_position() and steps < distance:
            steps += 1
            game.move_hero()  # передвижение героя в сторону курсора

        if pygame.mouse.get_focused():
            screen.blit(change_cursor(main_cursor), pygame.mouse.get_pos())

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == '__main__':
    menu()
