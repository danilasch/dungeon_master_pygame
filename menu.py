import pygame
import sys
from settings import *
from data import *
from main import screen, clock, main, change_cursor

# game+pygame settings
pygame.init()


class Button:
    def __init__(self, width, height, inactive=inactive_btn, active=active_btn,
                 action=None):  # width, height - велечины, выраженные в процентах
        self.width = round(width / 100 * WIDTH)
        self.height = round(height / 100 * HEIGHT)
        self.inactive = pygame.transform.scale(inactive, (
        round(width / 100 * WIDTH), round(height / 100 * HEIGHT)))
        self.active = pygame.transform.scale(active, (
        round(width / 100 * WIDTH), round(height / 100 * HEIGHT)))
        self.action = action

    def draw(self, x, y, message, font_size=30):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        self.x, self.y = round(x / 100 * WIDTH) - round(self.width / 2), round(y / 100 * HEIGHT) - round(
            self.height / 2)

        # Проверка курсора на кнопке
        if self.x < mouse[0] < self.x + self.width and self.y < mouse[1] < self.y + self.height:
            screen.blit(self.active, (self.x, self.y))
            if click[0] == 1:
                pygame.mixer.Sound.play(button_sound)
                pygame.time.delay(300)
                if self.action is not None:
                    self.action()
        else:
            screen.blit(self.inactive, (self.x, self.y))

        # Размер сообщения
        message_width, message_height = get_message_size(message, main_font, font_size)

        # Перенос сообщения на экран
        print_text(message, self.x + self.width // 2 - message_width // 2,
                   self.y + self.height // 2 - message_height // 2, font_size=font_size)
        
    def is_clicked(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        if self.x < mouse[0] < self.x + self.width and self.y < mouse[1] < self.y + self.height:
            if click[0] == 1:
                return True


class Checkbox:
    def __init__(self, side=5, inactive=inactive_box, active=active_box, action=None,
                 isactive=True):
        self.side = round(side / 100 * WIDTH)
        self.inactive = pygame.transform.scale(inactive, (self.side, self.side))
        self.active = pygame.transform.scale(active, (self.side, self.side))
        self.action = action
        self.isactive = isactive

    def draw(self, x, y, message=None, font_size=30):
        # x и y задаются в процентах, font_size задаётся для разрешения экрана 1920x1080
        x, y = round(x / 100 * WIDTH) - round(self.side / 2), round(y / 100 * HEIGHT) - round(
            self.side / 2)

        if self.isactive is True:
            screen.blit(self.active, (x, y))
        else:
            screen.blit(self.inactive, (x, y))

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if x < mouse[0] < x + self.side and y < mouse[1] < y + self.side:
            if click[0] == 1:
                pygame.time.delay(100)
                if self.isactive is True:
                    if self.action is not None:
                        self.action(False)
                    self.isactive = False
                    screen.blit(self.inactive, (x, y))
                else:
                    if self.action is not None:
                        self.action(True)
                    self.isactive = True
                    screen.blit(self.active, (x, y))
                pygame.mixer.Sound.play(button_sound)

        if message is not None:
            message_height = get_message_size(message, main_font, font_size)[1]

            print_text(message, x + self.side + round(WIDTH / 38, 4),
                       y + self.side // 2 - message_height // 2,
                       font_size=font_size)
            # 38,4 - коэффициент для адаптации расстояния от чекбокса


def music_off(off):
    if off is True:
        background_music.set_volume(0)
    else:
        background_music.set_volume(0.1)


def sounds_off(off):
    if off is True:
        button_sound.set_volume(0)
    else:
        button_sound.set_volume(0.5)


def settings():
    off_music = Checkbox(10, action=music_off, isactive=False)
    off_sound = Checkbox(10, action=sounds_off, isactive=False)
    back_btn = Button(13, 13)
    back_btn.draw(8, 8, 'Назад')

    while not back_btn.is_clicked():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill((100, 100, 100))

        off_music.draw(8, 25, 'Отключить музыку', 45)
        off_sound.draw(8, 45, 'Отключить звук', 45)
        back_btn.draw(8, 8, 'Назад')

        if pygame.mouse.get_focused():
            screen.blit(change_cursor(main_cursor), pygame.mouse.get_pos())

        pygame.display.flip()
        clock.tick(FPS)
    return


def achievements():
    back_btn = Button(13, 13)
    back_btn.draw(8, 8, 'Назад')

    while not back_btn.is_clicked():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
        screen.fill((100, 100, 100))

        print_text(f'Счёт предыдущей игры: {result["last-score"]}', HALF_WIDTH - get_message_size(f'Счёт предыдущей игры: {result["last-score"]}', main_font, 60)[0] // 2, 200, font_type=main_font, font_size=60)
        print_text(f'Максимальное кол-во очков: {result["record-score"]}', HALF_WIDTH - get_message_size(f'Максимальное кол-во очков: {result["record-score"]}', main_font, 60)[0] // 2, 300, font_type=main_font, font_size=60)
        print_text(f'Общее количество убийств: {result["total-kills"]}', HALF_WIDTH - get_message_size(f'Общее количество убийств: {result["total-kills"]}', main_font, 60)[0] // 2, 400, font_type=main_font, font_size=60)

        back_btn.draw(8, 8, 'Назад')

        if pygame.mouse.get_focused():
            screen.blit(change_cursor(main_cursor), pygame.mouse.get_pos())

            pygame.display.flip()
            clock.tick(FPS)
    return


def menu():
    pygame.mixer.Sound.play(background_music, loops=-1)

    start_btn = Button(17, 17, action=main)
    settings_btn = Button(17, 17, action=settings)
    quit_btn = Button(17, 17, action=sys.exit)
    achievements_btn = Button(6.5, 12, small_inactive_btn, small_active_btn, achievements)

    show = True
    while show:
        screen.blit(background, (0, 0))

        head_width, head_height = get_message_size('Dungeon Master', head_font, 150)
        print_text('Dungeon Master', HALF_WIDTH - head_width // 2, round(WIDTH / 10.8), (176, 0, 0),
                   head_font, 150)  # 10.8 - очередной коэффициент

        start_btn.draw(50, 50, 'Играть', 40)
        settings_btn.draw(50, 68, 'Настройки', 40)
        quit_btn.draw(50, 86, 'Выход', 40)
        achievements_btn.draw(95, 90, 'Достижения', 15)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        if pygame.mouse.get_focused():
            screen.blit(change_cursor(main_cursor), pygame.mouse.get_pos())

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
