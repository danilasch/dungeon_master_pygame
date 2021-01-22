from data import *
import random


def change_exits(tiles, coord, size, orientation):
    # при генерации новой комнаты какие-то выходы предыдущей комнаты
    # блокируются, а какие-то становятся дверями, чтобы открыться после
    # зачистки комнаты
    global exits
    if orientation == 'h':  # для горизонтальных выходов
        for tile in tiles:
            if tile.rect.right == coord + size:
                current_doors.add(tile)
                borders.add(tile)
                tile.image = tile_images['exit_h']
            else:
                borders.add(tile)
                tile.image = tile_images['floor']
    else:  # для вертикальных выходов
        for tile in tiles:
            if tile.rect.bottom == coord + size:
                current_doors.add(tile)
                borders.add(tile)
                tile.image = tile_images['exit_v']
            else:
                borders.add(tile)
                tile.image = tile_images['floor']

    exits.remove(*exits)


def change_doors(tiles):
    global current_doors
    current_doors.add(*tiles)


entries = pygame.sprite.Group()
current_entries = pygame.sprite.Group()
doors = pygame.sprite.Group()
current_doors = pygame.sprite.Group()
exits = pygame.sprite.Group()
borders = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, *groups):
        super().__init__(*groups)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class Room(pygame.sprite.Group):
    def __init__(self, filename, position, entry=None):
        super().__init__()
        filename = "data/maps/" + filename
        with open(filename, 'r') as mapFile:
            self.map = [line.strip() for line in mapFile]
        self.x, self.y = position
        self.height = len(self.map)
        self.width = len(self.map[0])
        self.entry, self.horizontals, self.verticals = [], [], []
        y = self.y
        self.entry = entry  # направление входа в комнату
        for j in range(len(self.map)):
            x = self.x
            for i in range(len(self.map[j])):
                if self.map[j][i] == '.':
                    Tile('parquet', x, y, self)
                elif self.map[j][i] == '#' or self.map[j][i] == '&':
                    Tile('wall', x, y, self, borders)
                elif self.map[j][i] == 'g':
                    Tile('sport', x, y, self)
                elif self.map[j][i] == 'e':
                    Tile('parquet', x, y, self, entries)
                elif self.map[j][i] == 'x':
                    Tile('parquet', x, y, self, exits)
                elif self.map[j][i] == 'h':
                    if self.entry == 'horizontal':
                        Tile('parquet', x, y, self)
                    else:
                        Tile('floor', x, y, self, borders)
                elif self.map[j][i] == 'v':
                    if self.entry == 'vertical':
                        Tile('parquet', x, y, self)
                    else:
                        Tile('floor', x, y, self, borders)
                elif self.map[j][i] == '-':
                    Tile('entry_h', x, y, self, doors)
                elif self.map[j][i] == '/':
                    Tile('entry_v', x, y, self, doors)
                x += TILE_WIDTH
            y += TILE_HEIGHT

    def get_tile(self, position):
        return self.map[position[1]][position[0]]

    def is_visible(self):  # метод определяет, видна ли комната на экране
        return (0 < self.x < WIDTH or 0 < self.x + self.width * TILE_WIDTH < WIDTH) and \
               (0 < self.y < HEIGHT or 0 < self.y + self.height * TILE_HEIGHT < HEIGHT)

    def move(self, camera):
        # передвижение комнаты относительно героя и смещение камеры
        self.x += camera.dx
        self.y += camera.dy
        for tile in self.sprites():
            camera.apply(tile)


class Map:
    def __init__(self):
        start_height, start_width = 11, 16
        corridor_width = 9
        x, y = (WIDTH - (start_width - 1) * TILE_WIDTH) // 2,\
               (HEIGHT - (start_height - 1) * TILE_HEIGHT) // 2
        corridor_pos = x + start_width * TILE_WIDTH, y + ((start_height // 2) - 2) * TILE_HEIGHT
        classroom_pos = corridor_pos[0] + TILE_WIDTH * corridor_width, y - TILE_HEIGHT

        self.map = [Room('start.txt', (x, y)),
                    Room('horizontal.txt', corridor_pos),
                    Room('classroom.txt', classroom_pos, 'horizontal')]
        # три начальные комнаты

    def render(self):
        # производим отрисовку только тех комнат,
        # которые находятся в поле видимости
        for room in self.map:
            if room.is_visible():
                room.draw(screen)

    def update(self):
        change_doors(doors)
        doors.remove(*doors)
        direction = random.choice((0, 1))
        room = self.map[-1]
        if direction == 0:  # новая комната и коридор к ней справа
            change_exits(exits, room.x, room.width * TILE_WIDTH, 'h')
            x, y = room.x, room.y
            width, height = room.width, room.height
            corridor_pos = x + width * TILE_WIDTH, y + (height // 2 - 2) * TILE_HEIGHT
            corridor = Room('horizontal.txt', corridor_pos)
            self.map.append(corridor)
            room_pos = corridor_pos[0] + corridor.width * TILE_WIDTH, y
            self.map.append(Room('classroom.txt', room_pos, 'horizontal'))

        else:  # новая комната и коридор к ней ниже
            change_exits(exits, room.y, room.height * TILE_HEIGHT, 'v')
            x, y = room.x, room.y
            width, height = room.width, room.height
            corridor_pos = x + (width // 2 - 2) * TILE_WIDTH, y + height * TILE_HEIGHT
            corridor = Room('vertical.txt', corridor_pos)
            self.map.append(corridor)
            room_pos = x, corridor_pos[1] + corridor.height * TILE_HEIGHT
            self.map.append(Room('classroom.txt', room_pos, 'vertical'))


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
        self.in_room = False

    def render(self, screen):
        self.map.render()
        self.hero.render(screen)

    def move_hero(self):
        x, y = self.hero.get_position()
        x += self.dx
        y += self.dy

        # герой не сможет зайти за границы borders
        if not pygame.sprite.spritecollideany(Hero((x, y)), borders):
            self.hero.rect.center = x, y
            self.camera.update(self.hero)
            for room in self.map.map:
                room.move(self.camera)

        # когда герой входит в какую-нибудь из комнат, комната
        # закрывается, пока её не зачистят
        if not self.in_room and pygame.sprite.spritecollideany(self.hero, entries):
            entries.remove(*entries)
            self.in_room = True
            self.lock_doors()

    def lock_doors(self):
        self.map.update()
        borders.add(*current_doors)

    def open_doors(self):
        borders.remove(*current_doors)
        for door in current_doors:
            door.image = tile_images['parquet']
        current_doors.remove(*current_doors)
        self.in_room = False


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
