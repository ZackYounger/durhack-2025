import pygame

# Optional: You can pass colours and fonts from outside instead of hardcoding them

class Button:
    def __init__(self, text, x, y, width, height, font, colour, hover_colour, text_colour, align="topleft"):
        self.text = text
        self.rect = pygame.Rect(0, 0, width, height)
        setattr(self.rect, align, (x, y))
        self.font = font
        self.colour = colour
        self.hover_colour = hover_colour
        self.text_colour = text_colour

    def draw(self, surface):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(surface, self.hover_colour if hovered else self.colour, self.rect, border_radius=12)

        text_surf = self.font.render(self.text, True, self.text_colour)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)
