# game.py
# A tiny Pygame game: move the player with arrow keys and collect coins.
# To enable streaming, put stream_game.py in the same folder and run:
#   python game.py --stream
# Then, on the *viewer* machine (or the same computer), run:
#   python stream_game.py --viewer --host 127.0.0.1 --port 9999
# British English spellings used in comments for consistency.

import sys
import random
import pygame

# Optional streaming toggle via CLI flag
ENABLE_STREAMING = ("--stream" in sys.argv)

try:
    from stream_game import StreamGame  # available if you copied stream_game.py next to this file
except ImportError:
    StreamGame = None
    ENABLE_STREAMING = False

WIDTH, HEIGHT = 800, 450
FPS = 60

PLAYER_SIZE = 28
PLAYER_SPEED = 5
COIN_SIZE = 14
COIN_COUNT = 10

BG_COLOUR = (16, 18, 22)
PLAYER_COLOUR = (60, 180, 255)
COIN_COLOUR = (255, 200, 60)
TEXT_COLOUR = (230, 230, 235)

def spawn_coins(rect):
    coins = []
    for _ in range(COIN_COUNT):
        x = random.randint(0, rect.width - COIN_SIZE)
        y = random.randint(0, rect.height - COIN_SIZE)
        coins.append(pygame.Rect(x, y, COIN_SIZE, COIN_SIZE))
    return coins

def main():
    pygame.init()
    pygame.display.set_caption("Mini Coin Collector")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    world_rect = screen.get_rect()
    player = pygame.Rect(WIDTH // 2 - PLAYER_SIZE // 2, HEIGHT // 2 - PLAYER_SIZE // 2, PLAYER_SIZE, PLAYER_SIZE)
    coins = spawn_coins(world_rect)
    score = 0
    time_left = 45.0  # seconds

    # STREAMING SERVER
    streamer = None
    if ENABLE_STREAMING and StreamGame is not None:
        # Start a streaming server listening on all interfaces so other computers can connect.
        # Use a different port if 9999 is taken.
        streamer = StreamGame(port=9999, max_clients=3, target_fps=60)
        streamer.start_server()
        print("[Streaming] Server started on 0.0.0.0:9999")

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        time_left = max(0.0, time_left - dt)

        # --- Input ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += PLAYER_SPEED

        player.x = max(0, min(WIDTH - PLAYER_SIZE, player.x + dx))
        player.y = max(0, min(HEIGHT - PLAYER_SIZE, player.y + dy))

        # --- Game logic ---
        collected = []
        for c in coins:
            if player.colliderect(c):
                collected.append(c)
                score += 1
        for c in collected:
            coins.remove(c)

        if not coins:
            coins = spawn_coins(world_rect)

        if time_left <= 0:
            running = False

        # --- Draw ---
        screen.fill(BG_COLOUR)
        # Coins
        for c in coins:
            pygame.draw.rect(screen, COIN_COLOUR, c, border_radius=4)
        # Player
        pygame.draw.rect(screen, PLAYER_COLOUR, player, border_radius=6)

        # HUD
        hud = f"Score: {score}   Time: {int(time_left):02d}s   Viewers: {streamer.client_count if streamer else 0}"
        txt = font.render(hud, True, TEXT_COLOUR)
        screen.blit(txt, (12, 10))

        pygame.display.flip()

        # --- Stream the current frame to any connected viewers (optional) ---
        if streamer:
            # It’s fine to call this each frame; it rate-limits internally.
            streamer.stream_surface(screen)

    # Tidy up
    if streamer:
        streamer.stop_server()
    pygame.quit()
    print(f"Final score: {score}")

if __name__ == "__main__":
    main()
