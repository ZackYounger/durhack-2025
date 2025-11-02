import sys
import pygame
import os
import subprocess
import json


# Import your screens
from Menu.main_menu import main_menu_loop
from Menu.host_menu import lobby_menu_loop
from Menu.join_menu import join_menu_loop


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
    # gross
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
            # lobby_menu_loop returns a tuple: (result, controller_data)
            result, controller_data = lobby_menu_loop(port=9999)   # choose your port

            if result == "start":
                try:
                    pygame.display.quit()
                except Exception as e:
                    print("Error")

                # Ensure controller_data is a dict
                if controller_data is None:
                    controller_data = {}

                try:
                    controllers_json = json.dumps(controller_data)
                except Exception:
                    controllers_json = str(controller_data)

                proc = run_subprocess("game/main.py", "--stream", "--controllers", controllers_json)
                print(f"[Host] Started game.py (PID {proc.pid}) with streaming on port 9999. Controllers: {len(controller_data) if controller_data else 0}")

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
                continue

            if isinstance(result, tuple) and result and result[0] == "connect":
                _, ip, port = result
                print("[Main] Launching viewer fullscreen…", flush=True)

                try:
                    pygame.display.quit()
                except Exception as e:
                    print(f"[Main] display.quit error: {e}", flush=True)

                proc = run_subprocess("viewer.py", "--host", ip, "--port", port)
                if proc:
                    print(f"[Join] Started viewer.py (PID {proc.pid}) for {ip}:{port}.", flush=True)
                else:
                    print("[Join] Failed to start viewer.py", flush=True)

                continue


        # Safety: cap loop tick
        clock.tick(60)

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    finally:
        pygame.quit()
