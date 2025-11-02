import pygame
import random
import level_manager
import player

WIDTH = 720
HEIGHT = 480
FPS = 60

## initialise pygame and create window (use fullscreen)
pygame.init()
pygame.joystick.init()  # === Controller subsystem ===

info = pygame.display.Info()
# use the actual display resolution for fullscreen
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("schlingo")
clock = pygame.time.Clock()     ## For syncing the FPS

gravity = 0.5

# --- Controller setup / hot-plug handling ---
joystick = None
def connect_first_joystick():
    global joystick
    joystick = None
    count = pygame.joystick.get_count()
    if count > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        try:
            name = joystick.get_name()
        except Exception:
            name = "Unknown Controller"
        print(f"[Controller] Connected: {name} (axes={joystick.get_numaxes()}, buttons={joystick.get_numbuttons()}, hats={joystick.get_numhats()})")
    else:
        print("[Controller] No controller detected")

connect_first_joystick()

# Deadzones / mapping (tweak if you like)
AXIS_DEADZONE = 0.30      # ignore tiny stick drift
HAT_ENABLED = True        # use D-Pad (hat) if present

# Common button mappings across Xbox/PS (these can vary by OS/driver, but this works well in practice):
BTN_JUMP_CANDIDATES = [0]            # A (Xbox) / Cross (PS)
BTN_DASH_CANDIDATES = [1, 5]         # B (Xbox)/Circle (PS), or RB/R1
BTN_ESCAPE_CANDIDATES = [7, 9]       # Start / Options as "pause/escape"
BTN_QUIT_COMBO = (6, 7)              # Back+Start (Xbox) or Share+Options (PS) to quit


temp_screens = [pygame.Rect(0, 0, WIDTH, HEIGHT),
                pygame.Rect(WIDTH + 20, -10, WIDTH * 1.2, HEIGHT * 1.2),
                pygame.Rect(WIDTH * 2.2 + 30, 10, WIDTH * .8, HEIGHT * .8)]

level = level_manager.Level()
level.create_new_level(temp_screens)
level_surface = pygame.Surface((level.world_size[0], level.world_size[1]))

player = player.Player(level.start_pos, level.block_width, level.border_walls, "SteamMan")

overview = False
tick = 0

def any_button_pressed(js, btn_indices):
    """Return True if any of the given button indices are currently pressed on js."""
    if js is None:
        return False
    n = js.get_numbuttons()
    for i in btn_indices:
        if 0 <= i < n and js.get_button(i):
            return True
    return False

def overlay_controller_on_keys(base_keys, js, plyr):
    """
    Start with keyboard get_pressed() and OR in controller state so
    player.update(...) can stay unchanged.
    """
    # Convert the immutable ScancodeSequence to a mutable list
    keys_list = list(base_keys)

    if js is None:
        return keys_list

    # --- Sticks ---
    # Left stick X/Y (typical: axis 0 = X, axis 1 = Y). Values in [-1.0, 1.0]
    try:
        lx = js.get_axis(0) if js.get_numaxes() > 0 else 0.0
        ly = js.get_axis(1) if js.get_numaxes() > 1 else 0.0
    except Exception:
        lx, ly = 0.0, 0.0

    # Horizontal movement
    if lx < -AXIS_DEADZONE:
        keys_list[plyr.controls["left"]] = True
    if lx > AXIS_DEADZONE:
        keys_list[plyr.controls["right"]] = True

    # Down (optional; many platformers ignore stick down—yours uses it as an input vector)
    if ly > AXIS_DEADZONE:
        keys_list[plyr.controls["down"]] = True

    # --- D-Pad (Hat) ---
    if HAT_ENABLED and js.get_numhats() > 0:
        hatx, haty = js.get_hat(0)  # (-1, 0, 1) per axis
        if hatx < 0:
            keys_list[plyr.controls["left"]] = True
        if hatx > 0:
            keys_list[plyr.controls["right"]] = True
        if haty < 0:  # hat up is -1, down is +1 (pygame uses screen coords)
            keys_list[plyr.controls["down"]] = True
        # If you want jump on D-Pad up, uncomment:
        # if haty > 0:
        #     keys_list[plyr.controls["jump"]] = True

    # --- Buttons: jump / dash ---
    if any_button_pressed(js, BTN_JUMP_CANDIDATES):
        keys_list[plyr.controls["jump"]] = True

    if any_button_pressed(js, BTN_DASH_CANDIDATES):
        keys_list[plyr.controls["dash"]] = True

    # --- Pause / Escape mapping ---
    if any_button_pressed(js, BTN_ESCAPE_CANDIDATES):
        keys_list[plyr.controls["esc"]] = True

    return keys_list


## Game loop
running = True
while running:
    clock.tick(FPS)

    # Keyboard base state
    kb_keys = pygame.key.get_pressed()

    # Events (also listen for controller hot-plug)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Toggle overview with keyboard (optional): press 'o'
        if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
            overview = not overview

        # Hot-plug controller
        if event.type == pygame.JOYDEVICEADDED:
            connect_first_joystick()
        if event.type == pygame.JOYDEVICEREMOVED:
            connect_first_joystick()

    # Allow quitting by keyboard quickly
    if kb_keys[pygame.K_ESCAPE] or kb_keys[pygame.K_q]:
        running = False

    # Quit combo on controller (Back+Start or Share+Options)
    if joystick and all(0 <= b < joystick.get_numbuttons() and joystick.get_button(b) for b in BTN_QUIT_COMBO):
        running = False

    # Merge controller state into keyboard keys for the player
    keys = overlay_controller_on_keys(kb_keys, joystick, player)

    level.draw(level_surface)

    player.update(tick, keys, gravity)
    player.draw(level_surface)

    if overview:
        # scale surface by factor (mini-map view)
        scaling_factor = .3
        scaled_surface = pygame.transform.scale(
            level_surface,
            (int(level_surface.get_width() * scaling_factor), int(level_surface.get_height() * scaling_factor))
        )
        screen.blit(scaled_surface, (0, 0))
    else:
        screen.blit(level_surface, (-level.padding, -level.padding))

    pygame.display.flip()
    tick += 1

pygame.quit()
