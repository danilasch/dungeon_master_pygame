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

    exits.empty()


# следующие 2 функции изменяют группы спрайтов
# при переходе в следующую комнату
def change_doors(tiles):
    global current_doors
    current_doors.add(*tiles)


def change_enemies(tiles):
    global current_enemies
    current_enemies.add(*tiles)


def get_length(x, y):
    return math.sqrt(x ** 2 + y ** 2)


ENEMY_DELAY = 1000
ENEMY_EVENT_TYPE = pygame.USEREVENT + 1
MAX_HEALTH = 10
MAX_ARMOR = 5
MAX_MANA = 100
HERO_GET_ARMOR = ENEMY_EVENT_TYPE + 1
HERO_GET_MANA = HERO_GET_ARMOR + 1
ARMOR_DELAY = 20000
MANA_DELAY = 10000
OPEN_DOORS_EVENT = pygame.event.Event(HERO_GET_MANA + 1)
entries = pygame.sprite.Group()
current_entries = pygame.sprite.Group()
doors = pygame.sprite.Group()
current_doors = pygame.sprite.Group()
exits = pygame.sprite.Group()
borders = pygame.sprite.Group()
enemies = pygame.sprite.Group()
current_enemies = pygame.sprite.Group()
shells = pygame.sprite.Group()
potions = pygame.sprite.Group()
current_object = None


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, *groups):
        super().__init__(*groups)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(pos_x, pos_y)


class Object(pygame.sprite.Sprite):
    """Класс объекта, которым может воспользоваться игрок.
    Объект закреплён за одной из комнат. В данной версии
    объектами являются сундуки и зелья"""
    def __init__(self, object_type, pos_x, pos_y, *groups):
        super().__init__(*groups)
        self.image = object_images[object_type]
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.name = object_type

    def open(self, new_image=None):
        if new_image:
            self.image = object_images[new_image]

        global current_object
        current_object = None

    def use(self, hero):
        if self.name == 'health':
            hero.heal(random.randint(2, 5))
        elif self.name == 'mana':
            hero.add_mana(random.randint(10, 50))

        self.kill()


class Wall(pygame.sprite.Sprite):
    """Класс для стен. Это особые тайлы, которые нужны
    в чисто декоративных целях. В три раза выше обычных тайлов."""
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

                elif self.map[j][i] == '~':
                    Tile('parquet', x, y, self)
                    enemies.add(CloseEnemy((x, y), 5, 1, 2))

                elif self.map[j][i] == '^':
                    Tile('parquet', x, y, self)
                    enemies.add(DistanceEnemy((x, y), 5, 1))

                elif self.map[j][i] == '0':
                    Tile('empty', x, y, self)

                elif self.map[j][i] == 'p':
                    Tile('parquet', x, y, self)
                    global current_object
                    current_object = Object('closed', x, y, self)

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
    """Класс игровой карты. Здесь храниться список комнат."""
    def __init__(self):
        start_height, start_width = 15, 16
        corridor_width = 9
        x, y = (WIDTH - (start_width - 1) * TILE_WIDTH) // 2,\
               (HEIGHT - (start_height - 1) * TILE_HEIGHT) // 2
        corridor_pos = x + start_width * TILE_WIDTH, y + ((start_height // 2) - 2) * TILE_HEIGHT
        classroom_pos = corridor_pos[0] + TILE_WIDTH * corridor_width, y - TILE_HEIGHT

        self.map = [Room('start.txt', (x, y)),
                    Room('horizontal.txt', corridor_pos),
                    Room('classroom1.txt', classroom_pos, 'h')]
        # три начальные комнаты

    def render(self):
        # производим отрисовку только тех комнат,
        # которые находятся в поле видимости
        for room in self.map:
            if room.is_visible():
                room.draw(screen)

    def update(self):  # добавление комнаты
        direction = random.choice((0, 1))
        room = self.map[-1]
        global current_object
        if direction == 0:  # новая комната и коридор к ней справа
            change_exits(exits, room.x, room.width * TILE_WIDTH, 'h')
            change_enemies(enemies)
            x, y = room.x, room.y
            width, height = room.width, room.height
            corridor_pos = x + width * TILE_WIDTH, y + (height // 2 - 1) * TILE_HEIGHT
            corridor = Room('horizontal.txt', corridor_pos)
            self.map.append(corridor)
            room_pos = corridor_pos[0] + corridor.width * TILE_WIDTH, y
            if current_object is None:
                self.map.append(Room(
                    f'classroom{random.choice(("1", "1", "1", "1", "2"))}.txt',
                    room_pos, 'h'))
            else:
                self.map.append(
                    Room(f'classroom{random.choice(("1", "1", "1", "1", "1"))}.txt',
                         room_pos, 'h'))

        else:  # новая комната и коридор к ней ниже
            change_exits(exits, room.y, room.height * TILE_HEIGHT, 'v')
            change_enemies(enemies)
            x, y = room.x, room.y
            width, height = room.width, room.height
            corridor_pos = x + (width // 2 - 2) * TILE_WIDTH, y + height * TILE_HEIGHT
            corridor = Room('vertical.txt', corridor_pos)
            self.map.append(corridor)
            room_pos = x, corridor_pos[1] + corridor.height * TILE_HEIGHT
            if current_object is None:
                self.map.append(
                    Room(f'classroom{random.choice(("1", "1", "1", "1", "2"))}.txt',
                         room_pos, 'v'))
            else:
                self.map.append(
                    Room(f'classroom{random.choice(("1", "1", "1", "1", "1"))}.txt',
                         room_pos, 'v'))


class BaseEntity(pygame.sprite.Sprite):
    """Базовый класс игровой сущности. От него наследуются
    классы игрока и врагов"""
    def __init__(self, position):
        super().__init__()
        self.radius = TILE_WIDTH * 7 // 10
        x, y = position
        # Rect для взаимодействия объекта со стенами
        self.rect = pygame.Rect(x, y + self.radius // 4, self.radius, self.radius // 2)

    def get_position(self):
        return self.rect.center


class Hero(BaseEntity):
    def __init__(self, position):
        super().__init__(position)
        x, y = position
        self.speed = 5
        self.health = MAX_HEALTH
        self.armor = MAX_ARMOR
        self.mana = MAX_MANA

        # Rect для отрисовки и улавливания снарядов противников
        self.body_rect = pygame.Rect(x, y - self.radius, self.radius, 2 * self.radius)

    def render(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), self.body_rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect)

    def attack(self):
        # метод создаёт снаряд и определяет направление его движения
        if self.mana:
            x1, y1, = self.rect.center
            x2, y2 = pygame.mouse.get_pos()
            vector = (x2 - x1, y2 - y1)
            length = get_length(*vector)
            shells.add(Shell(self.rect.center, vector, length, True, 2))
            if length != 0:
                self.mana -= 1

    def heal(self, value):
        if self.health + value > MAX_HEALTH:
            self.health = MAX_HEALTH
        else:
            self.health += value

    def hit(self, value):
        if self.armor > value:
            self.armor -= value
        else:
            value -= self.armor
            self.armor = 0
            if value < self.health:
                self.health -= value
            else:
                self.delete()

    def add_mana(self, value):
        if self.mana + value > MAX_MANA:
            self.mana = MAX_MANA
        else:
            self.mana += value

    def add_armor(self, value):
        if self.armor + value > MAX_ARMOR:
            self.armor = MAX_ARMOR
        else:
            self.armor += value

    def delete(self):
        pass


class BaseEnemy(BaseEntity):
    def __init__(self, position, health, power):
        super().__init__(position)
        x, y = position
        self.health = health
        self.power = power
        self.delay = 500
        self.is_alive = True

        # Rect для отрисовки и улавливания снарядов противников
        self.body_rect = pygame.Rect(x, y - self.radius, self.radius, 2 * self.radius)

    def render(self, screen):
        pygame.draw.rect(screen, (100, 100, 100), self.body_rect)

    def apply_camera(self, camera):
        self.body_rect.x += camera.dx
        self.body_rect.y += camera.dy
        camera.apply(self)

    def delete(self):
        self.is_alive = False
        self.body_rect.h = self.body_rect.h // 2
        if all(map(lambda enemy: not enemy.is_alive, current_enemies.sprites())):
            pygame.event.post(OPEN_DOORS_EVENT)

    def hit(self, value):
        if self.health > value:
            self.health -= value
        else:
            self.delete()


class CloseEnemy(BaseEnemy):
    """Класс противника, бегающего за героем и
    наносящего ближний урон."""
    def __init__(self, position, health, power, speed):
        super().__init__(position, health, power)
        self.speed = speed
        self.dx, self.dy = 0, 0
        self.steps = 0

    def move(self):
        if self.steps and self.is_alive:
            x, y = self.rect.topleft
            x += self.dx
            y += self.dy
            if not pygame.sprite.spritecollideany(BaseEntity((x, y)), borders):
                self.steps -= 1
                self.rect.topleft = x, y
                self.body_rect.topleft = x, y - self.radius

    def action(self, hero):
        # действием является пересчёт направления движения
        if self.is_alive:
            x1, y1, = self.rect.center
            x2, y2 = hero.get_position()
            vector = (x2 - x1, y2 - y1)
            length = get_length(*vector)
            if length > 20:
                self.dx, self.dy, self.steps = \
                    self.speed * vector[0] / length, \
                    self.speed * vector[1] / length, length // self.speed
            else:
                self.steps = 0
                hero.hit(self.power)


class DistanceEnemy(BaseEnemy):
    """Класс дальнобойного врага, который стреляет в героя,
    оставаясь на одном месте."""
    def __init__(self, position, health, power):
        super().__init__(position, health, power)

    def action(self, hero):
        # действием является расчёт траектории и запуск снаряда
        if self.is_alive:
            x1, y1, = self.rect.center
            x2, y2 = hero.get_position()
            vector = (x2 - x1, y2 - y1)
            length = get_length(*vector)
            shells.add(
                Shell(self.rect.center, vector, length, False, self.power))


class Game:
    """Служебный класс игры"""
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
        for shell in shells:
            shell.render(screen)

        frame_rect = pygame.rect.Rect(40, 5, 200, 33)
        points_rect = frame_rect.copy()

        # отрисовка элементов интерфейса
        screen.blit(interface_images['health'], (5, 5))
        points_rect.width = self.hero.health / MAX_HEALTH * frame_rect.width
        pygame.draw.rect(screen, pygame.Color("#fe0000"), points_rect)
        pygame.draw.rect(screen, pygame.Color("#464646"), frame_rect, width=2)
        print_text(f'{self.hero.health}/{MAX_HEALTH}', 70, 11, font_size=25)

        screen.blit(interface_images['armor'], (5, 45))
        frame_rect.y += 40
        points_rect.y += 40
        points_rect.width = self.hero.armor / MAX_ARMOR * frame_rect.width
        pygame.draw.rect(screen, pygame.Color("#c3c3c3"), points_rect)
        pygame.draw.rect(screen, pygame.Color("#464646"), frame_rect, width=2)
        print_text(f'{self.hero.armor}/{MAX_ARMOR}', 70, 51, font_size=25)

        screen.blit(interface_images['mana'], (5, 85))
        frame_rect.y += 40
        points_rect.y += 40
        points_rect.width = self.hero.mana / MAX_MANA * frame_rect.width
        pygame.draw.rect(screen, pygame.Color("#2196f3"), points_rect)
        pygame.draw.rect(screen, pygame.Color("#464646"), frame_rect, width=2)
        print_text(f'{self.hero.mana}/{MAX_MANA}', 70, 91, font_size=25)

        self.move_hero()
        self.move_enemies()
        for shell in shells:
            self.move_shell(shell)

    def move_hero(self):
        keys = pygame.key.get_pressed()

        if any(keys):
            x, y = self.hero.rect.topleft
            dx, dy = 0, 0
            if keys[pygame.K_w]:
                dy -= self.hero.speed
            if keys[pygame.K_s]:
                dy += self.hero.speed
            if keys[pygame.K_a]:
                if not dy:
                    dx -= self.hero.speed
                else:
                    dx -= self.hero.speed // 1.4
                    dy //= 1.4
            if keys[pygame.K_d]:
                if not dy:
                    dx += self.hero.speed
                else:
                    dx += self.hero.speed // 1.4
                    dy //= 1.4
            x += dx
            y += dy

            global current_object

            # герой не сможет зайти за границы borders
            if not pygame.sprite.spritecollideany(BaseEntity((x, y)), borders):
                # self.hero.rect.center = x, y
                self.camera.update(dx, dy)
                self.apply_camera()

            # когда герой входит в какую-нибудь из комнат, комната
            # закрывается, пока её не зачистят
            if not self.in_room and pygame.sprite.spritecollideany(self.hero, entries):
                entries.empty()
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

            # при наличии сундука в текущей комнате и пересечении с ним открыть сундук
            if not(current_object is None) and self.in_room and\
                    pygame.sprite.collide_rect(self.hero, current_object):
                self.doors_open = True
                Object(random.choice(("health", "mana")),
                       current_object.rect.x + TILE_WIDTH // 5,
                       current_object.rect.y + TILE_HEIGHT // 5,
                       self.map.map[-3], potions)
                current_object.open('open')
                self.open_doors()

    def apply_camera(self):
        for room in self.map.map:
            room.apply_camera(self.camera)
        for enemy in enemies:
            enemy.apply_camera(self.camera)
        for shell in shells:
            self.camera.apply(shell)

    def lock_doors(self):
        # закрытие дверей при входе в комнату
        door_close.play()
        change_doors(doors)
        doors.empty()
        self.change_doors_images('c', self.map.map[-1].entry, current_doors)
        self.map.update()
        borders.add(*current_doors)

    def change_doors_images(self, action, entry, group):
        # открывание и закрывание дверей наглядно
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
        # открытие дверей при успешной зачистке комнаты
        door_open.play()
        borders.remove(*current_doors)
        self.change_doors_images('o', self.map.map[-3].entry, current_doors)
        for enemy in current_enemies:
            enemy.delete()
        current_doors.empty()
        current_enemies.empty()
        self.in_room = False

    def move_enemies(self):
        for enemy in current_enemies:
            if isinstance(enemy, CloseEnemy):
                enemy.move()

    def move_shell(self, shell):
        x, y = shell.rect.center
        x += shell.dx
        y += shell.dy
        if shell.from_hero:
            for enemy in current_enemies:
                if enemy.is_alive and pygame.sprite.collide_circle(shell, enemy):
                    enemy.hit(shell.damage)
                    shells.remove(shell)
        else:
            if pygame.sprite.collide_circle(shell, self.hero):
                if self.hero.armor > shell.damage:
                    self.hero.armor -= shell.damage
                else:
                    damage = shell.damage - self.hero.armor
                    self.hero.armor = 0
                    self.hero.hit(damage)
                shells.remove(shell)
        if pygame.sprite.spritecollideany(shell, borders):
            shells.remove(shell)

        else:
            shell.rect.center = x, y


class Shell(pygame.sprite.Sprite):
    """Класс снаяряда. Одинаков для всех сущностей"""
    def __init__(self, pos, vector, length, from_hero, damage):
        super().__init__()
        self.speed = 7
        self.damage = damage
        self.dx = self.speed * vector[0] / length
        self.dy = self.speed * vector[1] / length
        x, y = pos
        self.from_hero = from_hero
        self.rect = pygame.rect.Rect(x, y, 10, 10)

    def render(self, screen):
        if self.from_hero:
            pygame.draw.circle(screen, pygame.Color("#2196f3"),
                               self.rect.center, self.rect.width // 2)
        else:
            pygame.draw.circle(screen, pygame.Color("Red"),
                               self.rect.center, self.rect.width // 2)


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
    def update(self, dx, dy):
        self.dx, self.dy = - dx, - dy
