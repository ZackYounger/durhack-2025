import pygame
from helpers import add_vecs, mult_vec_float, clamp, lerp
import random
from networkx import astar
import os

class TileSprites:
    def __init__(self, sprite_sheet_path, tile_size=16):
        self.tile_size = tile_size
        try:
            self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        except pygame.error:
            print(f"Could not load sprite sheet: {sprite_sheet_path}")
            self.sprite_sheet = None
            
        self.tiles = {}
        if self.sprite_sheet:
            self._extract_tiles()
    
    def _extract_tiles(self):
        """Extract individual tiles from the sprite sheet"""
        sheet_width = self.sprite_sheet.get_width()
        sheet_height = self.sprite_sheet.get_height()
        
        tiles_per_row = sheet_width // self.tile_size
        tiles_per_col = sheet_height // self.tile_size
        
        print(f"Sheet size: {sheet_width}x{sheet_height}")
        print(f"Tile size: {self.tile_size}")
        print(f"Tiles per row: {tiles_per_row}, tiles per col: {tiles_per_col}")
        
        for row in range(tiles_per_col):
            for col in range(tiles_per_row):
                x = col * self.tile_size
                y = row * self.tile_size
                tile_rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                tile_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                tile_surface.blit(self.sprite_sheet, (0, 0), tile_rect)
                self.tiles[(col, row)] = tile_surface
    
    def get_tile(self, col, row):
        """Get a specific tile by column and row"""
        return self.tiles.get((col, row), None)
    
    def scale_tile(self, tile, new_size):
        """Scale a tile to match block size"""
        if tile:
            return pygame.transform.scale(tile, (new_size, new_size))
        return None

class Level:

    def __init__(self):
        self.ideal_block_width = 16
        
        # Initialize tile sprites - try multiple possible paths
        possible_paths = [
            "Assets/Mossy Tileset/Mossy - TileSet.png",
            "../Assets/Mossy Tileset/Mossy - TileSet.png",
            "Mossy - TileSet.png"
        ]
        
        sprite_path = None
        for path in possible_paths:
            if os.path.exists(path):
                sprite_path = path
                print(f"Found sprite sheet at: {path}")
                break
        
        if sprite_path is None:
            print(f"Could not find sprite sheet in any of these locations:")
            for path in possible_paths:
                print(f"  {os.path.abspath(path)}")
            sprite_path = possible_paths[0]  # Use first path as fallback

        self.tile_sprites = TileSprites(sprite_path, 512)  # Each tile is 512x512 pixels
        print(f"Sprite sheet loaded: {self.tile_sprites.sprite_sheet is not None}")
        if self.tile_sprites.sprite_sheet:
            print(f"Number of tiles extracted: {len(self.tile_sprites.tiles)}")


    def create_new_level(self, screens):

        # get bounding box of all screens
        min_x = min(screen.left for screen in screens)
        max_x = max(screen.right for screen in screens)
        min_y = min(screen.top for screen in screens)
        max_y = max(screen.bottom for screen in screens)

        # world size + padding
        # `self.padding` here is pixels of padding around the combined screens.
        # Keep it explicit so changing padding doesn't accidentally mix units.
        self.padding = 16
        padding_px = self.padding
        origin_x = min_x - padding_px
        origin_y = min_y - padding_px
        # world size includes padding on both sides
        self.world_size = (max_x - min_x + padding_px * 2,
                           max_y - min_y + padding_px * 2)
        print(self.world_size)
        # number of blocks across/down (use integer division to get grid counts)
        num_blocks_wide = max(1, int(self.world_size[0] // self.ideal_block_width))
        num_blocks_tall = max(1, int(self.world_size[1] // self.ideal_block_width))
        self.level_size = [num_blocks_wide, num_blocks_tall]
        self.block_width = float(self.world_size[0]) / num_blocks_wide

        # initialize grid with zeros (0 = empty, 1 = wall). Using None
        # previously caused is_empty checks to misbehave when padding changed.
        self.level = [[0 for _ in range(num_blocks_wide)] for _ in range(num_blocks_tall)]

        def screen_pos_to_grid(pos):
            # convert world pixel (x,y) to grid indices using origin and block_width
            x, y = pos
            gx = int((x - origin_x) // self.block_width)
            gy = int((y - origin_y) // self.block_width)
            # clamp into grid bounds
            gx = max(0, min(num_blocks_wide - 1, gx))
            gy = max(0, min(num_blocks_tall - 1, gy))
            return (gx, gy)
        
        # line thickness in blocks (make lines N blocks wide)
        thickness = 10

        def mark_block(cx, cy):
            # mark a square of size `thickness` centered on (cx,cy)
            half = thickness // 2
            for ry in range(cy - half, cy + half + 1):
                for rx in range(cx - half, cx + half + 1):
                    if 0 <= ry < len(self.level) and 0 <= rx < len(self.level[0]):
                        self.level[ry][rx] = 1

        def draw_line(pos1, pos2):
            x1, y1 = screen_pos_to_grid(pos1)
            x2, y2 = screen_pos_to_grid(pos2)
            if x1 == x2:
                # vertical line
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    mark_block(x1, y)
            elif y1 == y2:
                # horizontal line
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    mark_block(x, y1)
            else:
                #error
                raise ValueError("Only horizontal or vertical lines are supported ... dickhead")
                #bingo bongo

        # draw border lines
        # first screen
        draw_line((screens[0].left, screens[0].top), (screens[0].left, screens[0].bottom))
        draw_line((screens[0].left, screens[0].bottom), (screens[1].left, screens[0].bottom))
        draw_line((screens[0].left, screens[0].top), (screens[1].left, screens[0].top))

        # middle screens
        for i in range(1, len(screens) - 1):
            draw_line((screens[i].left, screens[i-1].bottom), (screens[i].left, screens[i].bottom))
            draw_line((screens[i].left, screens[i-1].top), (screens[i].left, screens[i].top))
            draw_line((screens[i].left, screens[i].bottom), (screens[i+1].left, screens[i].bottom))
            draw_line((screens[i].left, screens[i].top), (screens[i+1].left, screens[i].top))

        # last connecting seam
        draw_line((screens[-1].left, screens[-2].bottom), (screens[-1].left, screens[-1].bottom))
        draw_line((screens[-1].left, screens[-2].top), (screens[-1].left, screens[-1].top))

        # last screen
        draw_line((screens[-1].right, screens[-1].top), (screens[-1].right, screens[-1].bottom))
        draw_line((screens[-1].left, screens[-1].bottom), (screens[-1].right, screens[-1].bottom))
        draw_line((screens[-1].left, screens[-1].top), (screens[-1].right, screens[-1].top))

        # Flood-fill from the grid edges to mark exterior area, then set
        # those cells to walls so the outside is filled in.
        from collections import deque

        rows = len(self.level)
        cols = len(self.level[0])
        visited = [[False] * cols for _ in range(rows)]
        q = deque()

        # enqueue boundary empty cells
        for x in range(cols):
            if self.level[0][x] == 0:
                visited[0][x] = True
                q.append((0, x))
            if self.level[rows-1][x] == 0:
                visited[rows-1][x] = True
                q.append((rows-1, x))
        for y in range(rows):
            if self.level[y][0] == 0:
                visited[y][0] = True
                q.append((y, 0))
            if self.level[y][cols-1] == 0:
                visited[y][cols-1] = True
                q.append((y, cols-1))

        while q:
            r, c = q.popleft()
            # mark outside as wall
            self.level[r][c] = 1
            for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and self.level[nr][nc] == 0:
                    visited[nr][nc] = True
                    q.append((nr, nc))


        # generate start (very left) and end (very right) points
        offset = 3

        start_corner = screen_pos_to_grid((screens[0].left, screens[0].bottom))
        self.start_pos = add_vecs(start_corner, [thickness // 2 + 1 + offset, -thickness // 2 - 1])

        self.end_corner = screen_pos_to_grid((screens[-1].right, screens[-1].bottom))
        self.end_pos = add_vecs(self.end_corner, [-thickness // 2 - 1 - offset, -thickness // 2 - 1])
        

        def unga_bunga():

            # New approach: Add 7-10 big blocks with specific requirements
            def generate_big_blocks():
                # Reduce number of blocks to make them actually big and avoid narrow shafts
                num_big_blocks = random.randint(5, 7)
                
                # Leave more blocks of space at start and end for safe zones
                start_buffer = 20
                end_buffer = 20
                usable_width = num_blocks_wide - start_buffer - end_buffer
                
                if usable_width <= 0:
                    return  # Not enough space
                
                # Create sections that cover the entire usable width
                # Divide usable width into sections for each block
                section_width = usable_width // num_big_blocks
                remaining_width = usable_width % num_big_blocks
                
                current_x = start_buffer
                # Initial floor height should be much higher (closer to bottom)
                # Floor height is distance FROM TOP, so higher number = closer to bottom
                max_reasonable_floor = num_blocks_tall - 15  # Leave at least 15 blocks from top
                previous_floor_height = random.randint(max_reasonable_floor - 7, max_reasonable_floor)
                
                for i in range(num_big_blocks):
                    # Calculate section boundaries
                    section_start = current_x
                    base_section_size = section_width
                    if i < remaining_width:  # Distribute remaining width to first few sections
                        base_section_size += 1
                    
                    # Block width: make them actually big to avoid narrow shafts
                    # Ensure blocks are substantial and cover most/all of their section
                    min_block_width = max(10, int(base_section_size * 0.8))  # At least 80% of section
                    max_block_width = min(25, base_section_size + 8)  # Allow more overlap for bigger blocks
                    block_width = random.randint(min_block_width, max_block_width)
                    
                    # Position block to fully cover section (no gaps)
                    block_x = section_start
                    # Allow small random offset but ensure full section coverage
                    if block_width > base_section_size:
                        max_offset = min(2, block_width - base_section_size)
                        block_x = max(start_buffer, section_start - random.randint(0, max_offset))
                    
                    # Floor height: ensure smooth transitions (max 5-7 block difference)
                    max_height_diff = random.randint(5, 7)
                    min_floor_height = max(max_reasonable_floor - 7, previous_floor_height - max_height_diff)
                    max_floor_height = min(max_reasonable_floor, previous_floor_height + max_height_diff)
                    
                    if min_floor_height <= max_floor_height:
                        floor_height = random.randint(min_floor_height, max_floor_height)
                    else:
                        floor_height = previous_floor_height
                    
                    # Calculate block position and dimensions
                    # Block starts from floor_height and goes to bottom
                    y = floor_height
                    block_height = num_blocks_tall - y
                    
                    # Double check - ensure we have at least 10 blocks from top
                    if y < 10:
                        y = 10
                        block_height = num_blocks_tall - y
                    
                    # Place the block
                    if block_height > 0:
                        for by in range(y, num_blocks_tall):
                            for bx in range(block_x, min(block_x + block_width, num_blocks_wide)):
                                if 0 <= by < num_blocks_tall and 0 <= bx < num_blocks_wide:
                                    # Don't overwrite start/end positions or existing walls
                                    if self.level[by][bx] == 0:
                                        self.level[by][bx] = 1
                    
                    previous_floor_height = floor_height
                    current_x = section_start + base_section_size

            # Generate the big blocks
            generate_big_blocks()

            # Horizontal traversal and platform improvements
            def improve_level_traversal():
                # Find floor level at each x position
                floor_heights = []
                for x in range(num_blocks_wide):
                    floor_y = num_blocks_tall - 1
                    for y in range(num_blocks_tall - 1, -1, -1):
                        if self.level[y][x] == 1:  # Found a wall/block
                            floor_y = y - 1  # Floor is one above the block
                            break
                    floor_heights.append(floor_y)
                
                # 1. Fix step-ups that are too high (>6 blocks)
                for x in range(1, len(floor_heights)):
                    current_floor = floor_heights[x]
                    prev_floor = floor_heights[x-1]
                    step_height = prev_floor - current_floor
                    
                    if step_height > 6:  # Step up is too high
                        # Add floating platform 1 tall, 3-5 wide
                        platform_width = random.randint(3, 5)
                        platform_y = current_floor + random.randint(3, 5)  # Intermediate height
                        platform_x = x - platform_width // 2
                        
                        # Place platform
                        for px in range(platform_x, platform_x + platform_width):
                            if 0 <= px < num_blocks_wide and 0 <= platform_y < num_blocks_tall:
                                if self.level[platform_y][px] == 0:
                                    self.level[platform_y][px] = 1
                
                # 2. Find gaps and add platforms where needed
                in_gap = False
                gap_start = 0
                for x in range(num_blocks_wide):
                    # Check if there's solid ground at this x position at floor level
                    has_solid_ground = False
                    floor_y = floor_heights[x]
                    if floor_y < num_blocks_tall - 1:
                        has_solid_ground = self.level[floor_y + 1][x] == 1
                    
                    if not has_solid_ground and not in_gap:
                        # Start of a gap
                        in_gap = True
                        gap_start = x
                    elif has_solid_ground and in_gap:
                        # End of a gap
                        gap_width = x - gap_start
                        
                        if gap_width > 6:  # Gap larger than 6 blocks needs platforms
                            # Add floating platforms across the gap
                            platform_width = random.randint(3, 5)
                            gap_between_platforms = random.randint(3, 4)
                            
                            # Calculate how many platforms we need
                            remaining_gap = gap_width - 2  # Leave space at edges
                            current_x = gap_start + 1
                            
                            # Find appropriate y level (between the two sides)
                            left_floor = floor_heights[max(0, gap_start - 1)]
                            right_floor = floor_heights[min(num_blocks_wide - 1, x)]
                            platform_y = min(left_floor, right_floor) + random.randint(2, 4)
                            
                            while current_x + platform_width < gap_start + gap_width - 1:
                                # Place platform
                                for px in range(current_x, min(current_x + platform_width, num_blocks_wide)):
                                    if 0 <= px < num_blocks_wide and 0 <= platform_y < num_blocks_tall:
                                        if self.level[platform_y][px] == 0:
                                            self.level[platform_y][px] = 1
                                
                                current_x += platform_width + gap_between_platforms
                                platform_y += random.randint(-1, 1)  # Slight y variation
                        
                        elif 1 <= gap_width <= 2:  # Small weird hole, make it bigger
                            new_width = random.randint(3, 5)
                            gap_center = gap_start + gap_width // 2
                            new_start = max(0, gap_center - new_width // 2)
                            new_end = min(num_blocks_wide, new_start + new_width)
                            
                            # Clear the hole to bottom
                            for hx in range(new_start, new_end):
                                for hy in range(10, num_blocks_tall):  # Keep top clearance
                                    if self.level[hy][hx] == 1:
                                        self.level[hy][hx] = 0
                        
                        in_gap = False
                
                # 3. Add a couple random holes with floating platforms
                num_holes = random.randint(2, 3)
                for _ in range(num_holes):
                    # Random position (avoid start/end buffers)
                    hole_x = random.randint(30, num_blocks_wide - 40)  # Use hardcoded safe zones
                    hole_width = random.randint(8, 12)
                    
                    # Clear hole to bottom
                    for hx in range(hole_x, min(hole_x + hole_width, num_blocks_wide)):
                        for hy in range(15, num_blocks_tall):  # Keep more top clearance
                            if self.level[hy][hx] == 1:
                                self.level[hy][hx] = 0
                    
                    # Add floating platforms across the hole
                    platform_count = random.randint(2, 3)
                    platform_width = random.randint(3, 5)
                    gap_between = random.randint(3, 4)
                    
                    current_x = hole_x + 2
                    base_y = random.randint(18, 25)
                    
                    for i in range(platform_count):
                        if current_x + platform_width < hole_x + hole_width - 2:
                            platform_y = base_y + random.randint(-2, 2)  # Slight y offset
                            
                            # Place platform
                            for px in range(current_x, current_x + platform_width):
                                if 0 <= px < num_blocks_wide and 0 <= platform_y < num_blocks_tall:
                                    if self.level[platform_y][px] == 0:
                                        self.level[platform_y][px] = 1
                            
                            current_x += platform_width + gap_between

            improve_level_traversal()

        def unga_bunga_2():
            import noise
            import math
            fildness = 0.1
            safe_zone_radius = 7  # Radius around start/end positions to keep clear

            seed = random.randint(0, 10000)

            # Calculate quarters of the level width
            quarter_width = self.level_size[0] // 4
            first_quarter_end = quarter_width
            last_quarter_start = self.level_size[0] - quarter_width

            scale = 7.0
            for y in range(self.level_size[1]):
                for x in range(self.level_size[0]):
                    # Check if this position is in a safe zone around start or end
                    start_distance = math.sqrt((x - self.start_pos[0])**2 + (y - self.start_pos[1])**2)
                    end_distance = math.sqrt((x - self.end_pos[0])**2 + (y - self.end_pos[1])**2)
                    
                    # Skip noise generation if we're in a safe zone
                    if start_distance <= safe_zone_radius or end_distance <= safe_zone_radius:
                        continue
                    
                    noise_val = noise.pnoise2(x/scale + seed, 
                                    y/scale + seed, 
                                    octaves=1, 
                                    persistence=1, 
                                    lacunarity=1, 
                                    repeatx=1024, 
                                    repeaty=1024, 
                                    base=0)
                    
                    # Create vertical bias - more land at bottom, less at top
                    # y = 0 is top, y = level_size[1]-1 is bottom
                    
                    # generate vertical progress from 0.0 (top) to 1.0 (bottom)
                    # smoothed between the n screens using a power curve
                    if x * self.block_width < screens[0].centerx:
                        vertical_progress = y / screens[0].height * self.block_width
                    for i in range(1, len(screens)):
                        if x * self.block_width > screens[i-1].centerx and x * self.block_width < screens[i].centerx:
                            xProgress = (x * self.block_width - screens[i-1].centerx) / (screens[i].centerx - screens[i-1].centerx)
                            vertical_progress = y / lerp(screens[i-1].height, screens[i].height, xProgress) * self.block_width
                    if x * self.block_width > screens[-1].centerx:
                        vertical_progress = y / screens[-1].height * self.block_width

                    vertical_progress **= 1.5  # 0.0 at top, 1.0 at bottom
                    
                    # Adjust threshold based on vertical position
                    # At top (progress=0): high threshold (hard to place blocks)
                    # At bottom (progress=1): low threshold (easy to place blocks)
                    biased_threshold = lerp(0.9, 0, vertical_progress)
                    
                    if noise_val > biased_threshold:
                        self.level[y][x] = 1
                    else:
                        self.level[y][x] = 0
                    #     if self.level[y][x] == 0:
                    #         self.level[y][x] = 1
                    # elif noise_val < fildness - fildness * (percentThroughX/(self.level_size[0]/2) - 1)**2:
                    #     if self.level[y][x] == 1:
                    #         self.level[y][x] = 0

        unga_bunga_2()

        self.level[self.start_pos[1]][self.start_pos[0]] = -1  # mark start point
        self.level[self.end_pos[1]][self.end_pos[0]] = -2  # mark end point


        # now generate border rects and render the level surface
        self.generate_border_walls()
        self.render_level()


    #Danial you lazy fuck
    #Thanks gpt
    def generate_border_walls(self):
        rows = len(self.level)
        cols = len(self.level[0])
        border_walls = []

        # Helper function to check if a cell is within bounds and empty
        def is_empty(r, c):
            return 0 <= r < rows and 0 <= c < cols and self.level[r][c] <= 0

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
        

        # Convert grid cell coordinates into screen-space Rects and store them.
        # Use the same conversion as render_level: top-left = (c * block_width, r * block_width).
        rects = [pygame.Rect(wall[0] * self.block_width, wall[1] * self.block_width, self.block_width, self.block_width) for wall in border_walls]
        self.border_walls = rects
        return rects

    def render_level(self):
        rendered_level = pygame.Surface(self.world_size)
        rendered_level.fill((50, 50, 50))  # Fill with background color

        epsilon = 0

        wall_count = 0
        for r, row in enumerate(self.level):
            for c, cell in enumerate(row):
                if cell == 1:  # Wall
                    wall_count += 1
                    # Try to use sprite tiles, fallback to solid colors
                    wall_tile = self._get_wall_tile(c, r)
                    if wall_tile:
                        scaled_tile = self.tile_sprites.scale_tile(wall_tile, int(self.block_width))
                        if scaled_tile:
                            rendered_level.blit(scaled_tile, (c * self.block_width, r * self.block_width))
                            if wall_count <= 3:  # Debug first few tiles
                                print(f"Successfully rendered sprite tile at ({c},{r})")
                        else:
                            # Fallback to solid color
                            rect = pygame.Rect(c * self.block_width, r * self.block_width, self.block_width + epsilon, self.block_width + epsilon)
                            pygame.draw.rect(rendered_level, (200, 200, 200), rect)
                            if wall_count <= 3:
                                print(f"Failed to scale tile at ({c},{r})")
                    else:
                        # Fallback to solid color
                        rect = pygame.Rect(c * self.block_width, r * self.block_width, self.block_width + epsilon, self.block_width + epsilon)
                        pygame.draw.rect(rendered_level, (200, 200, 200), rect)
                        if wall_count <= 3:
                            print(f"No wall tile returned for ({c},{r})")
                elif cell < 0:  # Start or end point
                    rect = pygame.Rect(c * self.block_width, r * self.block_width, self.block_width + epsilon, self.block_width + epsilon)
                    color = (50, 250, 50) if cell == -1 else (250, 50, 50)
                    pygame.draw.rect(rendered_level, color, rect)  # Draw start/end point

        border_wall_count = len(self.border_walls)
        # Comment out border wall drawing to see sprites underneath
        # for wall in self.border_walls:
        #     pygame.draw.rect(rendered_level, (100, 100 + random.randint(0, 50), 250), wall)  # Draw border walls differently
        
        print(f"Total walls in level array: {wall_count}")
        print(f"Total border walls: {border_wall_count}")
        self.rendered_level = rendered_level
    
    def _get_wall_tile(self, c, r):
        """
        Simple 4x4 autotiling system using the basic 16 tiles
        Based on the sprite sheet showing mossy terrain edges
        """
        if not self.tile_sprites.sprite_sheet:
            return None
        
        # Helper function to check if a position has a wall
        def has_wall(col, row):
            if row < 0 or row >= len(self.level) or col < 0 or col >= len(self.level[0]):
                return False  # Treat out-of-bounds as empty air (no wall)
            return self.level[row][col] == 1
        
        # Get 4-directional neighbors (cardinal directions only)
        top = has_wall(c, r-1)
        bottom = has_wall(c, r+1)
        left = has_wall(c-1, r)
        right = has_wall(c+1, r)
        tl = has_wall(c-1, r-1)
        tr = has_wall(c+1, r-1)
        bl = has_wall(c-1, r+1)
        br = has_wall(c+1, r+1)

        cum_card_walls = top + bottom + left + right
        cum_diag_walls = tl + tr + bl + br

        tile_coords = (1, 1)  # Default to isolated block

        # Determine tile based on neighbor configuration
        if cum_card_walls == 4:
            if cum_diag_walls == 4:
                tile_coords = (1, 1)  # Surrounded block
            elif cum_diag_walls == 3:
                if not tl:
                    tile_coords = (5, 1)
                elif not tr:
                    tile_coords = (4, 1)
                elif not bl:
                    tile_coords = (5, 0)
                elif not br:
                    tile_coords = (4, 0)
            elif cum_diag_walls == 2:
                if not tl and not tr:
                    tile_coords = (6, 0)
                elif not bl and not br:
                    tile_coords = (6, 3)
                elif not tl and not bl:
                    tile_coords = (6, 1)
                elif not tr and not br:
                    tile_coords = (6, 2)
                elif not tl and not br:
                    tile_coords = (6, 3)
                elif not tr and not bl:
                    tile_coords = (6, 2)
            elif cum_diag_walls == 1:
                if tr:
                    tile_coords = (5, 2)
                elif br:
                    tile_coords = (5, 3)
                elif tl:
                    tile_coords = (4, 2)
                elif bl:
                    tile_coords = (4, 3)
            elif cum_card_walls == 0:
                tile_coords = (5, 5)  # Surrounded block

        elif cum_card_walls == 3:
            if cum_diag_walls >= 2:
                if not top:
                    tile_coords = (1, 0)
                elif not bottom:
                    tile_coords = (1, 2)
                elif not left:
                    tile_coords = (0, 1)
                elif not right: 
                    tile_coords = (2, 1)
            elif cum_diag_walls == 1:
                if not top:
                    if not br:
                        tile_coords = (2, 4)
                    if not bl:
                        tile_coords = (3, 4)
                elif not bottom:
                    if not tr:
                        tile_coords = (2, 5)
                    if not tl:
                        tile_coords = (3, 5)
                elif not left:
                    if not tr:
                        tile_coords = (0, 5)
                    if not br:
                        tile_coords = (0, 4)
                elif not right:
                    if not tl:
                        tile_coords = (1, 5)
                    if not bl:
                        tile_coords = (1, 4)
            elif cum_diag_walls == 0:
                if top:
                    tile_coords = (5, 4)
                elif not bottom:
                    tile_coords = (5, 6)
                elif left:
                    tile_coords = (4, 5)
                elif right:
                    tile_coords = (6, 5)

        elif cum_card_walls == 2:
            # Check specific corners FIRST (adjacent missing sides)
            if not top and not left:  # Top-left corner
                if br:  # Bottom-right diagonal exists = normal corner
                    tile_coords = (0, 0)
                else:  # Bottom-right diagonal missing = inner corner
                    tile_coords = (4, 0)
            elif not top and not right:  # Top-right corner
                if bl:  # Bottom-left diagonal exists = normal corner
                    tile_coords = (2, 0)
                else:  # Bottom-left diagonal missing = inner corner
                    tile_coords = (6, 0)
            elif not bottom and not left:  # Bottom-left corner
                if tr:  # Top-right diagonal exists = normal corner
                    tile_coords = (0, 2)
                else:  # Top-right diagonal missing = inner corner
                    tile_coords = (4, 6)
            elif not bottom and not right:  # Bottom-right corner
                if tl:  # Top-left diagonal exists = normal corner
                    tile_coords = (2, 2)
                else:  # Top-left diagonal missing = inner corner
                    tile_coords = (6, 6)
            # Handle opposite sides missing (strips) - only if not a corner
            elif top and bottom and not left and not right:
                tile_coords = (3, 1)  # Vertical strip
            elif left and right and not top and not bottom:
                tile_coords = (1, 3)  # Horizontal strip

        elif cum_card_walls == 1:
            if top:
                tile_coords = (3, 2)
            elif bottom:
                tile_coords = (3, 0)
            elif left:
                tile_coords = (2, 3)
            elif right:
                tile_coords = (0, 3)

        elif cum_card_walls == 0:
            tile_coords = (3, 3)  # Isolated block

        return self.tile_sprites.get_tile(*tile_coords)

    def draw(self, screen):
        screen.blit(self.rendered_level, (0, 0))