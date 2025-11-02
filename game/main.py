import pygame
import random
import level_manager
import player
import sys
from Menu.stream_game import StreamGame
import json
import subprocess
import os

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

def run_subprocess(script_name, *args):
    """
    Launch a Python script in a separate process.
    Returns the Popen object (non-blocking).
    """
    # Resolve paths relative to this file
    here = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(here, "..", script_name)

    # Use the same Python interpreter that's running this program
    cmd = [sys.executable, script_path, *map(str, args)]

    # On Windows, you can add a new console window if you want:
    # gross
    creationflags = 0
    if os.name == "nt":
        # Uncomment if you want a new console for each subprocess:
        # creationflags = subprocess.CREATE_NEW_CONSOLE
        pass

    return subprocess.Popen(cmd, cwd=here, creationflags=creationflags)

# -- streaming --
is_streaming = "--stream" in sys.argv
streamer = None
controllers = {}
if is_streaming:
    try:
        controllers_idx = sys.argv.index("--controllers")
        controllers_json = sys.argv[controllers_idx + 1]
        controllers = json.loads(controllers_json)
    except (ValueError, IndexError):
        pass

    streamer = StreamGame(port=9999, max_clients=len(controllers) or 1)
    streamer.start_server()
    print(f"[Game] Streaming server started for {len(controllers)} players.")

    # Launch viewers
    base_port = 9999
    for i, controller_id in enumerate(controllers.keys()):
        port = base_port + i
        run_subprocess("viewer.py", "--host", "127.0.0.1", "--port", str(port))
        print(f"[Game] Started viewer for controller {controller_id} on port {port}")


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

    if is_streaming and streamer:
        streamer.stream_surface(screen)

    pygame.display.flip()       
    tick += 1

if is_streaming and streamer:
    streamer.stop_server()
    print("[Game] Streaming server stopped.")

pygame.quit()
