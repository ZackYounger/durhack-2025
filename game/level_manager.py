import pygame
from helpers import add_vecs, mult_vec_float
import random

class Level:

    def __init__(self):
        self.ideal_block_width = 4


    def create_new_level(self, screens):

        # get bounding box of all screens
        min_x = min(screen.left for screen in screens)
        max_x = max(screen.right for screen in screens)
        min_y = min(screen.top for screen in screens)
        max_y = max(screen.bottom for screen in screens)

        # world size + padding
        world_size = (max_x - min_x + self.ideal_block_width * 2,
                      max_y - min_y + self.ideal_block_width * 2)

        num_blocks_wide = world_size[0] // self.ideal_block_width
        num_blocks_tall = world_size[1] // self.ideal_block_width
        self.level_size = [num_blocks_wide, num_blocks_tall]
        self.block_width = world_size[0] / num_blocks_wide

        self.level = [[None for _ in range(num_blocks_wide)] for _ in range(num_blocks_tall)]

        #first do border

        # for r in range(num_blocks_tall):
        #     for c in range(num_blocks_wide):
        #         if r > 30 or c > 50:
        #             self.level[r][c] = 1
        #         else:
        #             self.level[r][c] = 0

        self.generate_border_walls()
        self.render_level(world_size)


    #Danial you lazy fuck
    #Thanks gpt
    def generate_border_walls(self):
        rows = len(self.level)
        cols = len(self.level[0])
        border_walls = []

        # Helper function to check if a cell is within bounds and empty
        def is_empty(r, c):
            return 0 <= r < rows and 0 <= c < cols and self.level[r][c] == 0

        # Directions to check neighboring cells (up, down, left, right)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]


        # Find all walls adjacent to empty space
        for r in range(rows):
            for c in range(cols):
                if self.level[r][c] == 1:  # Only check walls
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if is_empty(nr, nc):  # If neighboring cell is empty
                            border_walls.append((c, r))
                            break  # Stop checking other directions for this wall
        
        # this is what once was
        #self.border_walls = border_walls
        #return [pygame.Rect(*mult_vec_float(add_vecs(wall, [-self.level_size[0]/2]*2), self.block_width), self.block_width, self.block_width) for wall in border_walls]
        
        # Convert grid cell coordinates into screen-space Rects and store them.
        # Use the same conversion as render_level: top-left = (c * block_width, r * block_width).
        rects = [pygame.Rect(wall[0] * self.block_width, wall[1] * self.block_width, self.block_width, self.block_width) for wall in border_walls]
        self.border_walls = rects
        return rects

    def render_level(self, world_size):
        rendered_level = pygame.Surface(world_size)
        rendered_level.fill((50, 50, 50))  # Fill with background color

        for r, row in enumerate(self.level):
            for c, cell in enumerate(row):
                if cell == 1:  # Wall
                    rect = pygame.Rect(c * self.block_width, r * self.block_width, self.block_width, self.block_width)
                    pygame.draw.rect(rendered_level, (200, 200, 200), rect)  # Draw wall

        for wall in self.border_walls:
            pygame.draw.rect(rendered_level, (100, 100 + random.randint(0, 50), 250), wall)  # Draw border walls differently
        self.rendered_level = rendered_level

    def draw(self, screen):
        screen.blit(self.rendered_level, (0, 0))