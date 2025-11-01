import pygame

class TextField:
    def __init__(
        self,
        x, y, width, height,
        font,
        text_colour=(255, 255, 255),
        bg_colour=(20, 20, 20),
        border_colour=(120, 120, 120),
        active_border_colour=(255, 255, 255),
        placeholder="",
        align="center",
    ):
        """
        Minimal text field:
        - Click to focus
        - Type printable characters
        - Backspace/Delete
        - Left/Right arrows
        - Enter returns 'submit' from handle_event
        - Blinking caret
        """
        self.rect = pygame.Rect(0, 0, width, height)
        setattr(self.rect, align, (x, y))

        self.font = font
        self.text_colour = text_colour
        self.bg_colour = bg_colour
        self.border_colour = border_colour
        self.active_border_colour = active_border_colour
        self.placeholder = placeholder

        self.text = ""
        self.active = False
        self.padding = 12

        # caret
        self.cursor_pos = 0
        self._blink_on = False
        self._blink_timer = 0
        self._blink_period_ms = 530

    # -------- Public helpers --------
    def get_value(self):
        return self.text

    def set_value(self, value: str):
        self.text = value or ""
        self.cursor_pos = len(self.text)

    # -------- Event handling --------
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                # place caret roughly: choose end or start based on click
                cx = event.pos[0] - self.rect.x
                self.cursor_pos = len(self.text) if cx > self.rect.w // 2 else 0
                self._blink_on = True
                self._blink_timer = 0
            return None

        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            # Navigation
            if event.key == pygame.K_LEFT:
                if self.cursor_pos > 0: self.cursor_pos -= 1
                return None
            if event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.text): self.cursor_pos += 1
                return None
            if event.key == pygame.K_HOME:
                self.cursor_pos = 0
                return None
            if event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
                return None

            # Editing
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                return None
            if event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
                return None

            # Submit
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return "submit"

            # Characters
            if event.unicode and event.unicode.isprintable():
                ch = event.unicode
                self.text = self.text[:self.cursor_pos] + ch + self.text[self.cursor_pos:]
                self.cursor_pos += 1
                self._blink_on = True
                self._blink_timer = 0

        return None

    # -------- Update & Draw --------
    def update(self, dt_ms):
        if self.active:
            self._blink_timer += dt_ms
            if self._blink_timer >= self._blink_period_ms:
                self._blink_timer = 0
                self._blink_on = not self._blink_on
        else:
            self._blink_on = False
            self._blink_timer = 0

    def draw(self, surface):
        # background
        pygame.draw.rect(surface, self.bg_colour, self.rect, border_radius=10)
        # border
        border_col = self.active_border_colour if self.active else self.border_colour
        pygame.draw.rect(surface, border_col, self.rect, width=2, border_radius=10)

        # text or placeholder
        content = self.text if self.text else self.placeholder
        colour = self.text_colour if self.text else (140, 140, 140)
        txt_surf = self.font.render(content, True, colour)

        text_x = self.rect.x + self.padding
        text_y = self.rect.y + (self.rect.height - txt_surf.get_height()) // 2
        surface.blit(txt_surf, (text_x, text_y))

        # caret (only if focused and we have real text buffer)
        if self.active and self._blink_on:
            # width of text up to caret
            before = self.font.render(self.text[:self.cursor_pos], True, self.text_colour)
            caret_x = text_x + before.get_width()
            caret_top = self.rect.y + self.padding
            caret_bottom = self.rect.bottom - self.padding
            pygame.draw.line(surface, self.text_colour, (caret_x, caret_top), (caret_x, caret_bottom), 2)
