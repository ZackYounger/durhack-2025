import sys
import re
import ctypes
import argparse
import math
import pygame

# state for fullscreen toggle
is_fullscreen = True

_redraw_after_id = None
from ctypes import windll



def get_pixels_per_cm():
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication(sys.argv)
        screen = app.screens()[0]
        dpi = screen.physicalDotsPerInch()
        app.quit()
        print(max(1, int(round(dpi / 2.54))))
        return max(1, int(round(dpi / 2.54)))
    except Exception:
        # fallback: assume 96 dpi
        return int(round(96.0 / 2.54))

def parse_color(s):
    if not s:
        return pygame.Color('black')
    s = s.strip()
    if s.startswith('#'):
        s = s[1:]
    print(s)
    if re.fullmatch(r'[0-9a-fA-F]{6}', s):
        r = int(s[0:2], 16); g = int(s[2:4], 16); b = int(s[4:6], 16)
        return pygame.Color(r, g, b)
    try:
        return pygame.Color(s)
    except Exception:
        print("Invalid color string; using black.")
        return pygame.Color('black')

def main(colour_input="000000"):
    parser = argparse.ArgumentParser(description="1 cm checkerboard with colored border (Pygame).")
    parser.add_argument("--color", "-c", help="Border and one checker color (name or #RRGGBB). If omitted you'll be prompted.")
    args = parser.parse_args()

    pygame.init()
    info = pygame.display.Info()
    screen_w, screen_h = info.current_w, info.current_h

    # start fullscreen
    fullscreen = True
    windowed_size = (int(screen_w * 0.8), int(screen_h * 0.8))  # default windowed size

    def set_mode():
        nonlocal screen, screen_w, screen_h
        if fullscreen:
            screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            screen_w, screen_h = info.current_w, info.current_h
        else:
            screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
            screen_w, screen_h = windowed_size

    set_mode()
    pygame.display.set_caption("1 cm Checkerboard (Pygame)")

    chosen_color = parse_color(colour_input)
    white = pygame.Color(255, 255, 255)

    ppcm = get_pixels_per_cm()
    print(ppcm)
    border_px = ppcm
    square = ppcm

    clock = pygame.time.Clock()

    def draw():
        nonlocal screen_w, screen_h
        screen.fill(chosen_color)  # draw border color for full background

        inner_x = border_px
        inner_y = border_px
        inner_w = max(0, screen_w - 2 * border_px)
        inner_h = max(0, screen_h - 2 * border_px)
        if inner_w <= 0 or inner_h <= 0:
            pygame.display.flip()
            return

        cols = math.ceil(inner_w / square)
        rows = math.ceil(inner_h / square)

        for r in range(rows):
            y0 = inner_y + r * square
            for c in range(cols):
                x0 = inner_x + c * square
                color = chosen_color if (r + c) % 2 == 0 else white
                rect = pygame.Rect(x0, y0, square, square)
                pygame.draw.rect(screen, color, rect)

        pygame.display.flip()

    running = True
    draw()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F11:
                    if fullscreen:
                        # Save current fullscreen size as windowed size for restore
                        windowed_size = (max(400, int(screen_w * 0.8)), max(300, int(screen_h * 0.8)))
                    fullscreen = not fullscreen
                    set_mode()
                    draw()
            elif event.type == pygame.VIDEORESIZE:
                if not fullscreen:
                    screen_w, screen_h = event.w, event.h
                    windowed_size = (screen_w, screen_h)
                    screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
                    draw()

        # keep checker responsive (no continuous redraw unless needed)
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main("00ff15")
