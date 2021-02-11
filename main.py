import math
import menu
from classes import *

pygame.init()
pygame.display.set_caption('Dungeon Master')
pygame.mouse.set_visible(False)


def get_length(vector):  # вычисление длины вектора
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2)


# вычисление cкоростей по осям при
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
            # комната открывается ("зачищается" при нажатии ПКМ)
            if event.type == pygame.MOUSEBUTTONDOWN and game.in_room and event.button == 3:
                game.open_doors()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu.pause()

            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill(pygame.Color('black'))
        game.render(screen)

        game.move_hero()  # передвижение героя

        if pygame.mouse.get_focused():  # применение изменённого курсора
            screen.blit(change_cursor(main_cursor), pygame.mouse.get_pos())

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == '__main__':
    menu.menu()