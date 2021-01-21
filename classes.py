from data import *
import random

borders = pygame.sprite.Group()


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
        start_pos = (WIDTH - (start_width - 1) * TILE_WIDTH) // 2,\
                    (HEIGHT - (start_height - 1) * TILE_HEIGHT) // 2
        self.map = [Room('start.txt', start_pos)]

    def render(self):
        # производим отрисовку только тех комнат,
        # которые находятся в поле видимости
        for room in self.map:
            if room.is_visible:
                room.draw(screen)

    def update(self):
        direction = random.choice((0, 1))
        room = self.map[-1]
        if direction == 0:  # новая комната справа
            x, y = room.x, room.y
            width, height = room.width, room.height
            corridor_pos = x + width, y + width // 2 - TILE_HEIGHT
            corridor = Room('horizontal.txt', corridor_pos)
            self.map.append(corridor)
            room_pos = corridor.x + corridor.width, y
            self.map.append(Room('classroom.txt', room_pos))

        else:  # новая комната ниже
            x, y = room.x, room.y
            width, height = room.width, room.height
            corridor_pos = x + width // 2 - TILE_WIDTH, y + width
            corridor = Room('vertical.txt', corridor_pos)
            self.map.append(corridor)
            room_pos = x, corridor.y + corridor.height
            self.map.append(Room('classroom.txt', room_pos))


class Hero(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        x, y = position
        self.radius = TILE_WIDTH // 2
        x -= self.radius // 2
        y -= self.radius
        self.speed = 5
        self.rect = pygame.Rect(x, y, self.radius, 2 * self.radius)

    def get_position(self):
        return self.rect.center

    def render(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.rect)


class Game:  # служебный класс игры
    def __init__(self, game_map, hero, camera):
        self.map = game_map
        self.hero = hero
        self.camera = camera
        self.dx, self.dy = 0, 0

    def render(self, screen):
        self.map.render()
        self.hero.render(screen)

    def move_hero(self):
        x, y = self.hero.get_position()
        x += self.dx
        y += self.dy
        if not pygame.sprite.spritecollideany(Hero((x, y)), borders):
            self.hero.rect.center = x, y
            self.camera.update(self.hero)
            for room in self.map.map:
                room.move(self.camera)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)
        target.rect.x += self.dx
        target.rect.y += self.dy
