import pygame
import random
import level_manager
import player

WIDTH = 720
HEIGHT = 480
FPS = 60

## initialize pygame and create window
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("schlingo")
clock = pygame.time.Clock()     ## For syncing the FPS

gravity = 0.5

level = level_manager.Level()
level.create_new_level((WIDTH, HEIGHT), random.randint(0, 10000))

player = player.Player(level.block_width, level.border_walls)

tick = 0
## Game loop
running = True
while running:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
            running = False

    screen.fill((0, 0, 0))

    level.draw(screen)

    player.update(keys, tick, gravity)
    player.draw(screen)

    pygame.display.flip()       
    tick += 1
pygame.quit()
