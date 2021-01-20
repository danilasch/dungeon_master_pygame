import math
from menu import *
from data import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Dungeon Master')
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

borders = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, *groups):
        super().__init__(*groups)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class Room(pygame.sprite.Group):
    def __init__(self, filename, position):
        super().__init__()
        filename = "data/maps/" + filename
        with open(filename, 'r') as mapFile:
            self.map = [line.strip() for line in mapFile]
        self.x, self.y = position
        self.height = len(self.map)
        self.width = len(self.map[0])
        y = 0

        for j in range(len(self.map)):
            x = 0
            for i in range(len(self.map[j])):
                if self.map[j][i] == '.':
                    Tile('floor', x + self.x, y + self.y, self)
                elif self.map[j][i] == '#' or self.map[j][i] == '&':
                    Tile('wall', x + self.x, y + self.y, self, borders)
                elif self.map[j][i] == '@':
                    Tile('floor', x + self.x, y + self.y, self)
                    global hero
                    hero = Hero((x + self.x, y + self.y))
                x += TILE_WIDTH
            y += TILE_HEIGHT

    def get_tile(self, position):
        return self.map[position[1]][position[0]]

    def is_visible(self):
        return (0 < self.x < WIDTH or 0 < self.x + self.width * TILE_WIDTH < WIDTH) and \
               (0 < self.y < HEIGHT or 0 < 0 < self.y + self.height * TILE_HEIGHT < HEIGHT)

    def move(self, camera):
        self.x += camera.dx
        self.y += camera.dy
        for tile in self.sprites():
            camera.apply(tile)


class Map:
    height, width = 12, 12

    def __init__(self):
        start_height, start_width = 11, 16
        start_pos = (WIDTH - start_width * TILE_WIDTH) // 2,\
                    (HEIGHT - start_height * TILE_HEIGHT) // 2
        self.map = [Room('start.txt', start_pos)]

    def render(self):
        for room in self.map:
            if room.is_visible:
                room.draw(screen)

    def update(self, screen):
        pass


class Hero(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        x, y = position
        self.radius = TILE_WIDTH // 2
        self.speed = 5
        self.rect = pygame.Rect(x, y, self.radius, 2 * self.radius)

    def get_position(self):
        return self.rect.x, self.rect.y

    def set_position(self, position):
        if not pygame.sprite.spritecollideany(Hero(position), borders):
            self.rect.x, self.rect.y = position

    def render(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)


class Game:  # служебный класс игры
    def __init__(self, game_map, hero):
        self.map = game_map
        self.hero = hero
        self.dx, self.dy = 0, 0

    def render(self, screen):
        self.map.render()
        self.hero.render(screen)

    def move_hero(self):
        x, y = self.hero.get_position()
        x += self.dx
        y += self.dy
        self.hero.set_position((x, y))


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, size):
        self.dx = 0
        self.dy = 0
        self.size = size

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        # if obj.rect.x < -obj.rect.width:
        #     obj.rect.x += obj.rect.width * (self.size[0] + 1)
        # if obj.rect.x >= obj.rect.width * self.size[0]:
        #     obj.rect.x += -obj.rect.width * (self.size[0] + 1)

        obj.rect.y += self.dy
        # if obj.rect.y < -obj.rect.height:
        #     obj.rect.y += obj.rect.height * (self.size[0] + 1)
        # if obj.rect.y >= obj.rect.height * self.size[0]:
        #     obj.rect.y += -obj.rect.height * (self.size[0] + 1)

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


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

    # camera = Camera((WIDTH, HEIGHT))
    game = Game(Map(), Hero((HALF_WIDTH, HALF_HEIGHT)))
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

        # camera.update(game.hero)
        # print(camera.dx, camera.dy)
        # for room in game.map.map:
        #     room.move(camera)
        screen.fill(pygame.Color('black'))
        tiles_group.draw(screen)
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
