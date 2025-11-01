import sys
import pygame
import os
import subprocess


# Import your screens
from main_menu import main_menu_loop
from host_menu import lobby_menu_loop
from join_menu import join_menu_loop


def init_display_fullscreen():
    pygame.init()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption("DurHack 2025")
    return screen


def run_subprocess(script_name, *args):
    """
    Launch a Python script in a separate process.
    Returns the Popen object (non-blocking).
    """
    # Resolve paths relative to this file
    here = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(here, script_name)

    # Use the same Python interpreter that's running this program
    cmd = [sys.executable, script_path, *map(str, args)]

    # On Windows, you can add a new console window if you want:
    creationflags = 0
    if os.name == "nt":
        # Uncomment if you want a new console for each subprocess:
        # creationflags = subprocess.CREATE_NEW_CONSOLE
        pass

    return subprocess.Popen(cmd, cwd=here, creationflags=creationflags)



def main():
    # Create the window ONCE; sub-screens will reuse it
    screen = init_display_fullscreen()
    clock = pygame.time.Clock()

    # Simple state machine
    while True:
        # ---------- MAIN MENU ----------
        choice = main_menu_loop()   # expected: "host" or "join"
        if choice is None:
            # Defensive: if a loop returns None, just go back to main menu
            continue

        # ---------- HOST / LOBBY ----------
        if choice == "host":
            result = lobby_menu_loop(port=9999)   # choose your port
            # proc = run_subprocess("game.py", "--stream")
            # print(f"[Host] Started game.py (PID {proc.pid}) with streaming on port 9999.")
            
            if result == "start":
                try:
                    pygame.display.quit()
                except Exception as e:
                    print("Error")


                proc = run_subprocess("game.py", "--stream")  # game.py will stream the actual game
                print(f"[Host] Started game.py (PID {proc.pid}) with streaming on port 9999.")

                try:
                    pygame.display.init()
                    init_display_fullscreen()
                except Exception as e:
                    print("Error")
                continue

            elif result == "back":
                # Back to main menu
                continue

        # ---------- JOIN ----------
        elif choice == "join":
            result = join_menu_loop()
            if result == "back":
                # Back to main menu
                continue
            if isinstance(result, tuple) and result and result[0] == "connect":
                _, ip, port = result
                # TODO: Start your client connection here
                proc = run_subprocess("viewer.py", "--host", ip, "--port", port)
                print(f"[Join] Started viewer.py (PID {proc.pid}) for {ip}:{port}.")
                # After attempting connection, you can go to gameplay or back to main:
                # run_placeholder_gameplay(screen, clock)
                continue

        # Safety: cap loop tick
        clock.tick(60)

# def run_placeholder_gameplay(screen, clock):
#     """Tiny placeholder so you can see a 'game' screen after Start.
#     - ESC returns to main menu.
#     """
#     WHITE = (255, 255, 255)
#     BLACK = (0, 0, 0)
#     font = pygame.font.SysFont(None, 72)
#     w, h = screen.get_size()

#     while True:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit(); sys.exit()
#             if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
#                 return  # leave gameplay → main loop resumes at main menu

#         screen.fill(BLACK)
#         label = font.render("Gameplay placeholder — press ESC to return", True, WHITE)
#         rect = label.get_rect(center=(w // 2, h // 2))
#         screen.blit(label, rect)
#         pygame.display.flip()
#         clock.tick(60)

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    finally:
        pygame.quit()
