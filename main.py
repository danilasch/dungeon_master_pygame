import pygame
from settings import *
from menu import *
from data import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)

def change_cursor(cursor_image):
    cursor_image = pygame.image.load(cursor_image).convert_alpha()

    pygame.mouse.set_visible(False)

    return cursor_image

def main():
    background_music.set_volume(0)

    running = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill(pygame.Color('black'))
        
        if pygame.mouse.get_focused():
            screen.blit(change_cursor(main_cursor), pygame.mouse.get_pos())

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == '__main__':
    menu()