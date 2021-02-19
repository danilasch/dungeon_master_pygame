import math
import menu
from classes import *
import classes

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
    game = Game(Map(), Hero((WIDTH // 2, HEIGHT // 2)), Camera())
    running = True
    while running:
        for event in pygame.event.get():
            # комната открывается ("зачищается" при нажатии ПКМ)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.hero.attack()
                elif event.button == 3 and not game.in_room:
                    x, y = game.hero.rect.center
                    for potion in potions:
                        if pygame.mouse.get_pressed(3)[2] and get_length(
                                potion.rect.center[0] - x, potion.rect.center[1] - y) < 50:
                            potion.use(game.hero)
                            break

            if event.type == OPEN_DOORS_EVENT.type:
                game.open_doors()
                game.score += 1
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu.pause()

            if game.in_room and event.type == ENEMY_EVENT_TYPE:
                hero = game.hero
                for enemy in current_enemies:
                    enemy.action(hero)

            if game.in_room and event.type == ENEMY_EVENT_TYPE:
                hero = game.hero
                for enemy in current_enemies:
                    enemy.action(hero)

            if event.type == HERO_GET_ARMOR:
                game.hero.add_armor(1)

            if event.type == HERO_GET_MANA:
                game.hero.add_mana(5)

            if event.type == GAME_OVER_EVENT.type:
                return
                # menu.menu()

            if event.type == pygame.QUIT:
                if classes.current_score > result['record-score']:
                    result['record-score'] = classes.current_score

                with open(os.path.join('data', 'statistics.txt'), 'w') as f:
                    f.write(f'last-score={classes.current_score}\n')
                    f.write(f'record-score={result["record-score"]}\n')
                    f.write(f'total-kills={classes.total_kills}')

                sys.exit()

        screen.fill(pygame.Color('black'))
        game.render(screen)

        if pygame.mouse.get_focused():  # применение изменённого курсора
            screen.blit(change_cursor(main_cursor), pygame.mouse.get_pos())

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == '__main__':
    menu.menu()
