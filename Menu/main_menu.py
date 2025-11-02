import pygame
import sys
from Menu.button import Button  # Import your reusable Button class

pygame.init()

# ---------- Display ----------
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Main Menu")

# ---------- Fonts & Colours ----------
TITLE_FONT = pygame.font.SysFont(None, 80)
BUTTON_FONT = pygame.font.SysFont(None, 50)

WHITE = (255, 255, 255)
GRAY = (170, 170, 170)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

# ---------- Buttons (Centered) ----------
button_width, button_height = 250, 70
host_button = Button(
    text="Host",
    x=WIDTH // 2 - button_width // 2,
    y=HEIGHT // 2 - 100,
    width=button_width,
    height=button_height,
    font=BUTTON_FONT,
    colour=GRAY,
    hover_colour=DARK_GRAY,
    text_colour=WHITE,
)

join_button = Button(
    text="Add Screen",
    x=WIDTH // 2 - button_width // 2,
    y=HEIGHT // 2 + 20,
    width=button_width,
    height=button_height,
    font=BUTTON_FONT,
    colour=GRAY,
    hover_colour=DARK_GRAY,
    text_colour=WHITE,
)

# ---------- Main Menu Loop ----------
def main_menu_loop():
    """Displays the main menu. Returns 'host', 'join', or 'quit'."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if host_button.is_clicked(event):
                return "host"   # <- Hand control back to main to switch menus

            if join_button.is_clicked(event):
                return "join"

        # --- Draw Everything ---
        screen.fill(BLACK)

        title_surf = TITLE_FONT.render("Game Title", True, WHITE)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4))
        screen.blit(title_surf, title_rect)

        host_button.draw(screen)
        join_button.draw(screen)

        pygame.display.flip()

# For standalone testing
if __name__ == "__main__":
    result = main_menu_loop()
    print("Result =", result)
