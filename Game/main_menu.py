import pygame
import sys

pygame.init()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Menu Example")

TITLE_FONT = pygame.font.SysFont(None, 80)
BUTTON_FONT = pygame.font.SysFont(None, 50)

WHITE = (255, 255, 255)
GRAY = (170, 170, 170)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)

# Button setup
class Button:
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.colour = GRAY

    def draw(self, surface):
        # Hover effect
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(surface, DARK_GRAY, self.rect)
        else:
            pygame.draw.rect(surface, self.colour, self.rect)

        # Draw button text
        text_surf = BUTTON_FONT.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# Button positioning (centered)
button_width, button_height = 250, 70
host_button = Button("Host", WIDTH // 2 - button_width // 2, HEIGHT // 2 - 100, button_width, button_height)
join_button = Button("Join", WIDTH // 2 - button_width // 2, HEIGHT // 2 + 20, button_width, button_height)

def draw_menu():
    screen.fill(BLACK)

    # Title (change text later if you want)
    title_surface = TITLE_FONT.render("Game Title", True, WHITE)
    title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_surface, title_rect)

    # Draw buttons
    host_button.draw(screen)
    join_button.draw(screen)

def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            if host_button.is_clicked(event):
                print("Host Button Clicked")

            if join_button.is_clicked(event):
                print("Join Button Clicked")

        draw_menu()
        pygame.display.flip()

if __name__ == "__main__":
    main()
