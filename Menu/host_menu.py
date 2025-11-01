import pygame
import sys
import socket
from button import Button

# import time
# from stream_game import StreamGame

pygame.init()

# ---------- Screen / Fullscreen helper ----------
def _get_screen():
    surf = pygame.display.get_surface()
    if surf is not None:
        return surf
    info = pygame.display.Info()
    return pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)

screen = _get_screen()
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Lobby")


# streamer: StreamGame | None = None

# ---------- Fonts & Colours ----------
TITLE_FONT = pygame.font.SysFont(None, 80)
BUTTON_FONT = pygame.font.SysFont(None, 50)
SMALL_FONT = pygame.font.SysFont(None, 36)

WHITE = (255, 255, 255)
GRAY = (170, 170, 170)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

# ---------- Layout ----------
MARGIN = 40
ADD_BTN_W, ADD_BTN_H = 260, 70
START_BTN_W, START_BTN_H = 220, 70

# ---------- Networking ----------
DEFAULT_PORT = 9999

def _get_local_ip():
    ip = "0.0.0.0"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            pass
    return ip

# ---------- Controller setup ----------
pygame.joystick.init()

def _scan_existing_controllers(connected_map, players_list):
    """Initialise any currently connected controllers that aren’t tracked yet."""
    count = pygame.joystick.get_count()
    added = 0
    for i in range(count):
        js = pygame.joystick.Joystick(i)
        if not js.get_init():
            js.init()
        iid = js.get_instance_id()
        if iid not in connected_map:
            connected_map[iid] = js
            players_list.append(f"Player {len(players_list) + 1}")
            added += 1
    return added

# ---------- Draw ----------
def _draw_lobby(host_ip, host_port, add_btn, start_btn, players, awaiting_controller):
    screen.fill(BLACK)

    # Title
    title_surface = TITLE_FONT.render("Lobby", True, WHITE)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 8))
    screen.blit(title_surface, title_rect)

    # IP:PORT top-right
    ip_text = SMALL_FONT.render(f"Host: {host_ip}:{host_port}", True, WHITE)
    ip_rect = ip_text.get_rect(topright=(WIDTH - MARGIN, MARGIN))
    screen.blit(ip_text, ip_rect)

    # Add Player button (top-left-middle area)
    add_btn.draw(screen)

    # Player list (middle-left)
    left_x = MARGIN
    top_y = int(HEIGHT * 0.5) - 30 * len(players)  # roughly centre vertically as list grows
    for idx, name in enumerate(players):
        label = BUTTON_FONT.render(name, True, WHITE)
        label_rect = label.get_rect(topleft=(left_x, top_y + idx * 60))
        screen.blit(label, label_rect)

    # Listening hint
    if awaiting_controller:
        hint = SMALL_FONT.render("Listening for controller... connect one now.", True, WHITE)
        hint_rect = hint.get_rect(topleft=(MARGIN, add_btn.rect.bottom + 20))
        screen.blit(hint, hint_rect)

    # Start button (bottom-right)
    start_btn.draw(screen)
    pygame.display.flip()

# ---------- Public loop ----------
def lobby_menu_loop(port: int = DEFAULT_PORT):
    """
    Lobby screen:
    - Returns "start" when Start is clicked.
    - Returns "back" when ESC is pressed.
    """
    global streamer

    host_ip = _get_local_ip()
    host_port = port

    # if streamer is None:
    #     streamer = StreamGame(host=host_ip, port=host_port, max_clients=3, target_fps=60)
    #     streamer.start_server()

    # Buttons
    add_player_btn = Button(
        text="Add Player",
        x=MARGIN,
        y=int(HEIGHT * 0.3),
        width=ADD_BTN_W,
        height=ADD_BTN_H,
        font=BUTTON_FONT,
        colour=GRAY,
        hover_colour=DARK_GRAY,
        text_colour=WHITE,
        align="topleft",
    )

    start_btn = Button(
        text="Start",
        x=WIDTH - MARGIN - START_BTN_W,
        y=HEIGHT - MARGIN - START_BTN_H,
        width=START_BTN_W,
        height=START_BTN_H,
        font=BUTTON_FONT,
        colour=GRAY,
        hover_colour=DARK_GRAY,
        text_colour=WHITE,
        align="topleft",
    )

    # State
    connected_joysticks = {}   # instance_id -> Joystick
    players = []               # ["Player 1", "Player 2", ...]
    awaiting_controller = False

    clock = pygame.time.Clock()

    # Allow hotplug events to come through
    pygame.event.set_allowed([
        pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN,
        pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED
    ])

    # Optional: pick up any controllers already present
    _scan_existing_controllers(connected_joysticks, players)

    while True:
        for event in pygame.event.get():
            # Window close
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Esc → back to main menu
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # if streamer:
                #     streamer.stop_server()
                return "back"

            # Buttons
            if add_player_btn.is_clicked(event):
                awaiting_controller = True
                # If a controller is already present, register it immediately
                if _scan_existing_controllers(connected_joysticks, players) > 0:
                    awaiting_controller = False

            if start_btn.is_clicked(event):
                print("start button is clicked")
                # Stop lobby stream so game.py can take over the same port
                # if streamer:
                #     streamer.stop_server()
                return "start"


            # Controller hotplug
            if event.type == pygame.JOYDEVICEADDED:
                js = pygame.joystick.Joystick(event.device_index)
                if not js.get_init():
                    js.init()
                iid = js.get_instance_id()
                if iid not in connected_joysticks:
                    connected_joysticks[iid] = js
                    players.append(f"Player {len(players) + 1}")
                    print(f"Controller connected: {js.get_name()} -> {players[-1]}")
                awaiting_controller = False

            if event.type == pygame.JOYDEVICEREMOVED:
                iid = event.instance_id
                if iid in connected_joysticks:
                    del connected_joysticks[iid]
                    # Keep labels stable; do not renumber existing players.

        _draw_lobby(host_ip, host_port, add_player_btn, start_btn, players, awaiting_controller)

        # if streamer:
        #     streamer.stream_surface(screen)
        
        clock.tick(60)

# Standalone test
if __name__ == "__main__":
    result = lobby_menu_loop()
    print("Lobby result =", result)
