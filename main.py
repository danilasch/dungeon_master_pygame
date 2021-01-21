import math
from menu import *
from classes import *

pygame.init()
pygame.display.set_caption('Dungeon Master')
pygame.mouse.set_visible(False)


def get_length(vector):  # вычисление длины вектора
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2)


# вычисление коростей по осям при
# движении в сторону курсора
def calculate_motion(start_pos, final_pos, speed):
    x1, y1, = start_pos
    x2, y2 = final_pos
    vector = (x2 - x1, y2 - y1)
    length = get_length(vector)
    return speed * vector[0] / length, speed * vector[1] / length


def main():
    background_music.set_volume(0)

    game = Game(Map(), Hero(pygame.mouse.get_pos()), Camera())
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                # при движении мыши пересчитывается траектория движения персонажа
                if pygame.mouse.get_pos() != game.hero.get_position():
                    game.dx, game.dy = calculate_motion(
                        game.hero.get_position(), pygame.mouse.get_pos(), game.hero.speed)

            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill(pygame.Color('black'))
        game.render(screen)

        if pygame.mouse.get_pos() != game.hero.get_position():
            game.move_hero()  # передвижение героя в сторону курсора

        if pygame.mouse.get_focused():  # применение изменённого курсора
            screen.blit(change_cursor(main_cursor), pygame.mouse.get_pos())

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == '__main__':
    menu()
