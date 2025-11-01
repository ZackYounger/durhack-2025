import pygame
import sys
from button import Button
from text_field import TextField

pygame.init()

# ---------- Screen (reuse existing or fullscreen) ----------
def _get_screen():
    surf = pygame.display.get_surface()
    if surf is not None:
        return surf
    info = pygame.display.Info()
    return pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)

screen = _get_screen()
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Join")

# ---------- Fonts & Colours ----------
TITLE_FONT = pygame.font.SysFont(None, 80)
BUTTON_FONT = pygame.font.SysFont(None, 50)
FIELD_FONT  = pygame.font.SysFont(None, 48)

WHITE = (255, 255, 255)
GRAY = (170, 170, 170)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
FIELD_BG = (25, 25, 25)

MARGIN = 40
FIELD_W, FIELD_H = 520, 64
GAP = 16
CONNECT_W, CONNECT_H = 220, 70

def join_menu_loop():
    """
    Join screen:
    - Two centred text fields (Server IP, Port) stacked vertically.
    - Connect button bottom-right.
    Returns:
        ("connect", ip_str, port_str) on connect
        "back" on ESC
    """
    # Position fields (centred horizontally, stacked)
    ip_field = TextField(
        x=WIDTH // 2, y=(HEIGHT // 2) - (FIELD_H + GAP//2),
        width=FIELD_W, height=FIELD_H,
        font=FIELD_FONT,
        text_colour=WHITE,
        bg_colour=FIELD_BG,
        border_colour=(90, 90, 90),
        active_border_colour=WHITE,
        placeholder= "Server IP (e.g., 192.168.1.10)",
        align="center",
        # validator=None,  # allow any printable for IP/hostname
    )

    port_field = TextField(
        x=WIDTH // 2, y=(HEIGHT // 2) + (FIELD_H + GAP//2),
        width=FIELD_W, height=FIELD_H,
        font=FIELD_FONT,
        text_colour=WHITE,
        bg_colour=FIELD_BG,
        border_colour=(90, 90, 90),
        active_border_colour=WHITE,
        placeholder="Port (e.g., 5000)",
        align="center",
        # validator=_digits_only,  # digits only
    )

    connect_btn = Button(
        text="Connect",
        x=WIDTH - MARGIN - CONNECT_W,
        y=HEIGHT - MARGIN - CONNECT_H,
        width=CONNECT_W,
        height=CONNECT_H,
        font=BUTTON_FONT,
        colour=GRAY,
        hover_colour=DARK_GRAY,
        text_colour=WHITE,
        align="topleft",
    )

    # Back button (top-left)
    BACK_BTN_W, BACK_BTN_H = 180, 60
    back_btn = Button(
        text="Back",
        x=MARGIN,
        y=MARGIN,
        width=BACK_BTN_W,
        height=BACK_BTN_H,
        font=BUTTON_FONT,
        colour=GRAY,
        hover_colour=DARK_GRAY,
        text_colour=WHITE,
        align="topleft",
    )


    # Make the first field active by default
    ip_field.active = True

    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back"
            
            if back_btn.is_clicked(event):
                return "back"

            if connect_btn.is_clicked(event):
                return ("connect", ip_field.get_value().strip(), port_field.get_value().strip())

            # Route events to fields
            submit_ip = ip_field.handle_event(event)
            submit_port = port_field.handle_event(event)

            # Tab / Shift+Tab focus switch
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    # Reverse
                    if port_field.active:
                        port_field.active = False; ip_field.active = True
                    else:
                        ip_field.active = False; port_field.active = True
                else:
                    if ip_field.active:
                        ip_field.active = False; port_field.active = True
                    else:
                        port_field.active = False; ip_field.active = True

            # Enter behaviour: move to next, or connect if on port
            if submit_ip == "submit":
                ip_field.active = False
                port_field.active = True
            if submit_port == "submit":
                return ("connect", ip_field.get_value().strip(), port_field.get_value().strip())

            # Clicking the connect button
            if connect_btn.is_clicked(event):
                return ("connect", ip_field.get_value().strip(), port_field.get_value().strip())

            # Clicking outside: focus set by click is handled inside TextField already

        # Update blinking carets
        ip_field.update(dt)
        port_field.update(dt)

        # --------- Draw ---------
        screen.fill(BLACK)

        title = TITLE_FONT.render("Join", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 6))
        screen.blit(title, title_rect)

        ip_field.draw(screen)
        port_field.draw(screen)

        connect_btn.draw(screen)
        back_btn.draw(screen)

        pygame.display.flip()

# Standalone run
if __name__ == "__main__":
    result = join_menu_loop()
    print("Join result:", result)
