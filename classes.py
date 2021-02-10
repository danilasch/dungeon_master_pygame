from data import *
import random
import math


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


def change_enemies(tiles):
    global current_enemies
    current_enemies.add(*tiles)


ENEMY_DELAY = 500
ENEMY_EVENT_TYPE = pygame.USEREVENT + 1
MAX_HEALTH = 10
MAX_DEFENCE = 5
MAX_MANA = 100
HERO_GET_ARMOR = pygame.USEREVENT + 1
HERO_GET_MANA = pygame.USEREVENT + 1
ARMOR_DELAY = 20000
MANA_DELAY = 10000
entries = pygame.sprite.Group()
current_entries = pygame.sprite.Group()
doors = pygame.sprite.Group()
current_doors = pygame.sprite.Group()
exits = pygame.sprite.Group()
borders = pygame.sprite.Group()
enemies = pygame.sprite.Group()
current_enemies = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, *groups):
        super().__init__(*groups)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class Wall(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, *groups):
        super().__init__(*groups)
        pos_y -= 2 * TILE_HEIGHT
        self.image = wall_images[tile_type]
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
        self.entry = entry  # направление входа в комнату

        doors_number = 0
        y = self.y

        # заполнение комнаты тайлами
        for j in range(len(self.map)):
            x = self.x
            for i in range(len(self.map[j])):
                if self.map[j][i] == '.':
                    Tile('parquet', x, y, self)

                elif self.map[j][i] == '&':
                    Tile('wall', x, y, self, borders)

                elif self.map[j][i] == 'g':
                    Tile('sport', x, y, self)

                elif self.map[j][i] == 'e':
                    Tile('parquet', x, y, self, entries)

                elif self.map[j][i] == 'x':
                    Tile('parquet', x, y, self, exits)

                elif self.map[j][i] == 'h':
                    if self.entry == 'h':
                        Tile('parquet', x, y, self)
                    else:
                        Tile('floor', x, y, self, borders)

                elif self.map[j][i] == 'v':
                    if self.entry == 'v':
                        Tile('parquet', x, y, self)
                    else:
                        Wall('classwall', x, y, self, borders)

                elif self.map[j][i] == '-':
                    Tile('entry_h', x, y, self, doors)

                elif self.map[j][i] == '/':
                    Wall('entry_v' + str(doors_number), x, y, self, doors)
                    doors_number += 1

                elif self.map[j][i] == 'l':
                    Wall('class' + str(random.randint(1, 4)), x, y, self, borders)

                elif self.map[j][i] == 'w':
                    Wall('classwall', x, y, self, borders)

                elif self.map[j][i] == '+':
                    Tile('sport', x, y, self)
                    enemies.add(BaseEnemy((x, y), 10, 1))

                elif self.map[j][i] == '0':
                    Tile('empty', x, y, self)
                x += TILE_WIDTH
            y += TILE_HEIGHT

    def is_visible(self):  # метод определяет, видна ли комната на экране
        return (0 < self.x < WIDTH or 0 < self.x + self.width * TILE_WIDTH < WIDTH or
                self.x < 0 and self.x + self.width * TILE_WIDTH > WIDTH) and \
               (0 < self.y < HEIGHT or 0 < self.y + self.height * TILE_HEIGHT < HEIGHT or
                self.y <= 0 and self.y + self.height * TILE_HEIGHT >= HEIGHT)

    def apply_camera(self, camera):
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
        classroom_pos = corridor_pos[0] + TILE_WIDTH * corridor_width, y - 3 * TILE_HEIGHT

        self.map = [Room('start.txt', (x, y)),
                    Room('horizontal.txt', corridor_pos),
                    Room('classroom.txt', classroom_pos, 'h')]
        # три начальные комнаты

    def render(self):
        # производим отрисовку только тех комнат,
        # которые находятся в поле видимости
        for room in self.map:
            if room.is_visible():
                room.draw(screen)

    def update(self):
        direction = random.choice((0, 1))
        room = self.map[-1]
        if direction == 0:  # новая комната и коридор к ней справа
            change_exits(exits, room.x, room.width * TILE_WIDTH, 'h')
            change_enemies(enemies)
            x, y = room.x, room.y
            width, height = room.width, room.height
            corridor_pos = x + width * TILE_WIDTH, y + (height // 2 - 1) * TILE_HEIGHT
            corridor = Room('horizontal.txt', corridor_pos)
            self.map.append(corridor)
            room_pos = corridor_pos[0] + corridor.width * TILE_WIDTH, y
            self.map.append(Room('classroom.txt', room_pos, 'h'))

        else:  # новая комната и коридор к ней ниже
            change_exits(exits, room.y, room.height * TILE_HEIGHT, 'v')
            x, y = room.x, room.y
            width, height = room.width, room.height
            corridor_pos = x + (width // 2 - 2) * TILE_WIDTH, y + height * TILE_HEIGHT
            corridor = Room('vertical.txt', corridor_pos)
            self.map.append(corridor)
            room_pos = x, corridor_pos[1] + corridor.height * TILE_HEIGHT
            self.map.append(Room('classroom.txt', room_pos, 'v'))


class BaseEntity(pygame.sprite.Sprite):

    def __init__(self, position):
        super().__init__()
        self.radius = TILE_WIDTH * 7 // 10
        x, y = position
        # Rect для взаимодействия объекта со стенами
        self.rect = pygame.Rect(x, y + self.radius // 2, self.radius, self.radius // 2)

    def get_position(self):
        return self.rect.center


class Hero(BaseEntity):
    def __init__(self, position):
        super().__init__(position)
        x, y = position
        self.speed = 5
        self.health = MAX_HEALTH
        self.defence = MAX_DEFENCE
        self.mana = MAX_MANA

        # Rect для отрисовки и улавливания снарядов противников
        self.body_rect = pygame.Rect(x, y - self.radius, self.radius, 2 * self.radius)

    def render(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.body_rect)


class BaseEnemy(BaseEntity):
    def __init__(self, position, health, power):
        super().__init__(position)
        x, y = position
        self.health = health
        self.power = power
        self.speed = 4
        self.dx, self.dy = 0, 0
        self.delay = 500
        self.steps = 0
        self.isalive = True

        # Rect для отрисовки и улавливания снарядов противников
        self.body_rect = pygame.Rect(x, y - self.radius, self.radius, 2 * self.radius)

    def move(self):
        if self.steps and self.isalive:
            x, y = self.get_position()
            x += self.dx
            y += self.dy
            if not pygame.sprite.spritecollideany(BaseEntity((x, y)), borders):
                self.steps -= 1
                self.rect.center = x, y
                self.body_rect.center = x, y

    def go_to(self, position):
        if self.isalive:
            x1, y1, = self.rect.center
            x2, y2 = position
            vector = (x2 - x1, y2 - y1)
            length = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
            if length != 0:
                self.dx, self.dy, self.steps = \
                    self.speed * vector[0] / length,\
                    self.speed * vector[1] / length, length // self.speed
            else:
                self.steps = 0

    def attack(self, position):
        pass

    def render(self, screen):
        pygame.draw.rect(screen, (100, 100, 100), self.body_rect)

    def apply_camera(self, camera):
        self.body_rect.x += camera.dx
        self.body_rect.y += camera.dy
        camera.apply(self)

    def delete(self):
        self.isalive = False
        self.body_rect.y += self.body_rect.h // 2


class Game:  # служебный класс игры
    def __init__(self, game_map, hero, camera):
        self.map = game_map
        self.hero = hero
        self.camera = camera
        self.dx, self.dy = 0, 0
        self.in_room = False
        self.doors_open = False
        pygame.time.set_timer(ENEMY_EVENT_TYPE, ENEMY_DELAY)
        pygame.time.set_timer(HERO_GET_ARMOR, ARMOR_DELAY)
        pygame.time.set_timer(HERO_GET_MANA, MANA_DELAY)

    def render(self, screen):
        self.map.render()
        self.hero.render(screen)
        for enemy in current_enemies:
            enemy.render(screen)

        frame_rect = pygame.rect.Rect(40, 5, 200, 33)
        points_rect = frame_rect.copy()

        screen.blit(interface_images['health'], (5, 5))
        points_rect.width = self.hero.health / MAX_HEALTH * frame_rect.width
        pygame.draw.rect(screen, pygame.Color("#fe0000"), points_rect)
        pygame.draw.rect(screen, pygame.Color("#464646"), frame_rect, width=2)
        print_text(f'{self.hero.health}/{MAX_HEALTH}', 70, 11, font_size=25)

        screen.blit(interface_images['defence'], (5, 45))
        frame_rect.y += 40
        points_rect.y += 40
        points_rect.width = self.hero.defence / MAX_DEFENCE * frame_rect.width
        pygame.draw.rect(screen, pygame.Color("#c3c3c3"), points_rect)
        pygame.draw.rect(screen, pygame.Color("#464646"), frame_rect, width=2)
        print_text(f'{self.hero.defence}/{MAX_DEFENCE}', 70, 51, font_size=25)

        screen.blit(interface_images['mana'], (5, 85))
        frame_rect.y += 40
        points_rect.y += 40
        points_rect.width = self.hero.mana / MAX_MANA * frame_rect.width
        pygame.draw.rect(screen, pygame.Color("#2196f3"), points_rect)
        pygame.draw.rect(screen, pygame.Color("#464646"), frame_rect, width=2)
        print_text(f'{self.hero.mana}/{MAX_MANA}', 70, 91, font_size=25)

    def move_hero(self):
        keys = pygame.key.get_pressed()

        if any(keys):
            x, y = self.hero.get_position()
            dx, dy = 0, 0
            if keys[pygame.K_w]:
                dy -= self.hero.speed
            if keys[pygame.K_s]:
                dy += self.hero.speed
            if keys[pygame.K_a]:
                if not dy:
                    dx -= self.hero.speed
                else:
                    dx -= self.hero.speed // 1.41
                    dy //= 1.41
            if keys[pygame.K_d]:
                if not dy:
                    dx += self.hero.speed
                else:
                    dx += self.hero.speed // 1.41
                    dy //= 1.41

            x += dx
            y += dy

            # герой не сможет зайти за границы borders
            if not pygame.sprite.spritecollideany(BaseEntity((x, y)), borders):
                self.hero.rect.center = x, y
                self.camera.update(self.hero)
                for room in self.map.map:
                    room.apply_camera(self.camera)
                for enemy in enemies:
                    enemy.apply_camera(self.camera)
                    enemy.go_to((x, y))

            # когда герой входит в какую-нибудь из комнат, комната
            # закрывается, пока её не зачистят
            if not self.in_room and pygame.sprite.spritecollideany(self.hero, entries):
                entries.remove(*entries)
                self.in_room = True
                self.lock_doors()

            #  открытие (скрытие) дверей при контакте с ними
            if not self.doors_open and pygame.sprite.spritecollideany(self.hero, doors):
                self.doors_open = True
                door_open.play()
                self.change_doors_images('o', self.map.map[-1].entry, doors)

            #  возвращение дверей в закрытое положение
            elif self.doors_open and not pygame.sprite.spritecollideany(self.hero, doors):
                self.doors_open = False
                door_close.play()
                if not self.in_room:
                    self.change_doors_images('c', self.map.map[-1].entry, doors)

    def lock_doors(self):
        door_close.play()
        change_doors(doors)
        doors.remove(*doors)
        self.change_doors_images('c', self.map.map[-1].entry, current_doors)
        self.map.update()
        borders.add(*current_doors)

    def change_doors_images(self, action, entry, group):
        if action == 'c':
            if entry == 'h':
                for sprite in group:
                    sprite.image = tile_images['entry_h']
            else:
                for i in range(len(group.sprites())):
                    group.sprites()[i].image = wall_images['entry_v' + str(i)]

        else:
            if entry == 'h':
                for sprite in group:
                    sprite.image = tile_images['parquet']
            else:
                for sprite in group:
                    sprite.image = wall_images['parquet']

    def open_doors(self):
        door_open.play()
        borders.remove(*current_doors)
        self.change_doors_images('o', self.map.map[-3].entry, current_doors)
        for enemy in current_enemies:
            enemy.delete()
        current_doors.remove(*current_doors)
        current_enemies.remove(*current_enemies)
        self.in_room = False

    def move_enemies(self):
        for enemy in current_enemies:
            enemy.move()


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
