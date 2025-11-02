import pygame
import random
import level_manager
import player

WIDTH = 720
HEIGHT = 480
FPS = 60

## initialize pygame and create window (use fullscreen)
pygame.init()
info = pygame.display.Info()
# use the actual display resolution for fullscreen
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("schlingo")
clock = pygame.time.Clock()     ## For syncing the FPS

gravity = 0.5

temp_screens = [pygame.Rect(0, 0, WIDTH, HEIGHT),
                pygame.Rect(WIDTH + 20, -10, WIDTH * 1.2, HEIGHT * 1.2),
                pygame.Rect(WIDTH * 2.2 + 30, 10, WIDTH * .8, HEIGHT * .8)]

level = level_manager.Level()
level.create_new_level(temp_screens)
level_surface = pygame.Surface((level.world_size[0], level.world_size[1]))

player = player.Player(level.start_pos, level.block_width, level.border_walls, "SteamMan")

overview = False
tick = 0
## Game loop
running = True
while running:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
            running = False

    level.draw(level_surface)

    player.update(tick, keys, gravity)
    player.draw(level_surface)

    if overview:
        #scale surface by half
        scaling_factor = .3
        scaled_surface = pygame.transform.scale(level_surface, (level_surface.get_width() * scaling_factor, level_surface.get_height() * scaling_factor))
        screen.blit(scaled_surface, (0,0))
    else:
        screen.blit(level_surface, (-level.padding, -level.padding))


    pygame.display.flip()       
    tick += 1
pygame.quit()
