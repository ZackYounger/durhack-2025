import pygame
import os

from .helpers import add_vecs, mult_vec_float

epsilon = 5

class PlayerSprites:
    def __init__(self, sprite_folder_path, player_name):
        self.sprite_folder = sprite_folder_path
        self.player_name = player_name
        self.sprites_loaded = False
        self.animation_files = {}
        self.animation_frames = {}
        
        self._load_animation_files()
    
    def _load_animation_files(self):
        """Load individual animation files from the sprite folder"""
        animation_mappings = {
            'idle': f'{self.player_name}_idle.png',
            'run': f'{self.player_name}_run.png', 
            'walk': f'{self.player_name}_walk.png',
            'jump': f'{self.player_name}_jump.png',
            'hurt': f'{self.player_name}_hurt.png',
            'death': f'{self.player_name}_death.png'
        }
        
        for anim_name, filename in animation_mappings.items():
            file_path = os.path.join(self.sprite_folder, filename)
            try:
                sprite_sheet = pygame.image.load(file_path).convert_alpha()
                self.animation_files[anim_name] = sprite_sheet
                print(f"Loaded {anim_name} animation: {filename}")
            except pygame.error:
                print(f"Could not load {anim_name} animation: {file_path}")
        
        if self.animation_files:
            self.sprites_loaded = True
            self._extract_animation_frames()
    
    def _extract_animation_frames(self):
        """Extract individual frames from each animation sprite sheet"""
        for anim_name, sprite_sheet in self.animation_files.items():
            frames = []
            sheet_width = sprite_sheet.get_width()
            sheet_height = sprite_sheet.get_height()
            
            # Assume sprites are arranged horizontally, detect frame size
            # Most character sprites are around 48x48 or 64x64 pixels
            frame_height = sheet_height
            frame_width = frame_height  # Assume square frames initially
            
            # Try to detect frame width by looking for common sizes
            common_frame_sizes = [48, 64, 32, 96]
            for size in common_frame_sizes:
                if sheet_width % size == 0 and size <= sheet_height:
                    frame_width = size
                    break
            
            # If still not found, use height as width
            if sheet_width % frame_width != 0:
                frame_width = frame_height
            
            num_frames = sheet_width // frame_width
            
            print(f"  {anim_name}: {sheet_width}x{sheet_height} -> {num_frames} frames of {frame_width}x{frame_height}")
            
            for i in range(num_frames):
                x = i * frame_width
                frame_rect = pygame.Rect(x, 0, frame_width, frame_height)
                frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame_surface.blit(sprite_sheet, (0, 0), frame_rect)
                frames.append(frame_surface)
            
            self.animation_frames[anim_name] = frames
    
    def get_animation_frames(self, animation_name):
        """Get all frames for a specific animation"""
        return self.animation_frames.get(animation_name, [])
    
    def scale_sprite(self, sprite, new_width, new_height):
        """Scale a sprite to match player size"""
        if sprite:
            return pygame.transform.scale(sprite, (new_width, new_height))
        return None

class Player:
    def __init__(self, start_index, block_width, border_walls, name):
        self.name = name
        self.jump_strength = 15
        self.dash_strength = 20
        self.dashCooldown = 60
        self.lastDashTick = 0

        self.acc_scaling = 1.5
        self.horizontal_vel_drag = 0.7
        self.vertical_vel_drag = 0.95
        
        self.width = 20
        self.height = 45

        self.grounded = False

        self.block_width = block_width
        self.border_walls = border_walls

        self.pos = mult_vec_float(start_index, block_width)
        self.vel = [0, 0]
        self.acc = [0, 0]
        
        # Initialize player sprites using player name and folder structure
        possible_base_paths = [
            f"Assets/Mossy Tileset/chars/{self.name}",
            f"../Assets/Mossy Tileset/chars/{self.name}",
            f"Assets/Player/{self.name}",
            f"../Assets/Player/{self.name}",
        ]
        
        sprite_base_path = None
        for path in possible_base_paths:
            if os.path.exists(path):
                sprite_base_path = path
                print(f"Found player sprite folder for '{self.name}' at: {path}")
                break
        
        if sprite_base_path is None:
            print(f"Could not find player sprite folder for '{self.name}' in any of these locations:")
            for path in possible_base_paths:
                print(f"  {os.path.abspath(path)}")
            sprite_base_path = possible_base_paths[0]  # Use first path as fallback
        
        self.player_sprites = PlayerSprites(sprite_base_path, self.name)
        print(f"Player '{self.name}' sprites loaded: {self.player_sprites.sprites_loaded}")
        if self.player_sprites.sprites_loaded:
            print(f"Number of animation files loaded for '{self.name}': {len(self.player_sprites.animation_files)}")
            
        # Animation state
        self.current_frame = 0
        self.animation_timer = 0
        self.facing_right = True
        self.current_state = "idle"  # idle, run, jump, hurt, death
        
        # Preload specific animation sprites
        self._preload_animations()

        self.controls = {
                    "down": pygame.K_s,
                    "right": pygame.K_d,
                    "left": pygame.K_a,
                    "jump": pygame.K_w,
                    "dash": pygame.K_k,
                    "esc": pygame.K_ESCAPE}

    def update(self, tick, keys, gravity):
        self.acc = [0, gravity]

        #movement
        if self.grounded and keys[self.controls["jump"]]:
            self.vel[1] = -self.jump_strength
        
        acc_inp = [keys[self.controls["right"]] - keys[self.controls["left"]],
						keys[self.controls["down"]]]
		
        self.acc = add_vecs(self.acc, mult_vec_float(acc_inp, self.acc_scaling))
        
        # Store original horizontal acceleration to check for wall hanging
        self.horizontal_input = acc_inp[0] * self.acc_scaling
        
        
        # Update animation frame counter
        self.current_frame += 1

        # Store previous grounded state for better physics
        was_grounded = self.grounded
        
        self.vel = add_vecs(self.acc, self.vel)
        self.vel[0] *= self.horizontal_vel_drag
        
        # Only apply vertical drag if not grounded to prevent bouncing
        if not was_grounded:
            self.vel[1] *= self.vertical_vel_drag
        
        self.pos = add_vecs(self.vel, self.pos)

        # Update facing direction and animation
        if self.vel[0] > 0:
            self.facing_right = True
        elif self.vel[0] < 0:
            self.facing_right = False


        #collisions
        self.hitbox = pygame.Rect(self.pos[0] - self.width/2, self.pos[1] - self.height/2, self.width, self.height)

        self.grounded = False

        # iterative collision resolution: handle up to a few passes to avoid
        # snapping into other walls when multiple collisions occur
        max_iters = 2
        it = 0
        while it < max_iters:
            wall_collisions = self.hitbox.collidelistall(self.border_walls)
            self.collide = True if len(wall_collisions) > 0 else False
            if not wall_collisions:
                break

            for wallIndex in wall_collisions:
                wall = self.border_walls[wallIndex]
                # wall is a pygame.Rect
                wall_center = [wall.left + wall.width/2, wall.top + wall.height/2]
                distance = add_vecs(self.pos, [-wall_center[0], -wall_center[1]])

                # choose axis with larger penetration to resolve (0=x, 1=y)
                dr = 0 if abs(distance[0]) > abs(distance[1]) else 1
                perp = (dr + 1) % 2

                # player's half-sizes
                player_half_dr = (self.width / 2) if dr == 0 else (self.height / 2)
                player_half_perp = (self.height / 2) if perp == 1 else (self.width / 2)

                # Use actual rectangle collision detection instead of distance-based
                if self.hitbox.colliderect(wall):
                    # Calculate overlap more accurately
                    overlap_x = min(self.hitbox.right, wall.right) - max(self.hitbox.left, wall.left)
                    overlap_y = min(self.hitbox.bottom, wall.bottom) - max(self.hitbox.top, wall.top)
                    
                    # Resolve along the axis with smaller overlap (most likely direction of approach)
                    if overlap_x < overlap_y:
                        # Horizontal collision - resolve horizontally
                        if self.pos[0] < wall_center[0]:
                            # player left of wall -> move player to left of wall
                            self.pos[0] = wall.left - self.width/2
                        else:
                            # player right of wall -> move player to right of wall
                            self.pos[0] = wall.right + self.width/2
                        self.vel[0] = 0  # Stop horizontal velocity
                    else:
                        # Vertical collision - resolve vertically
                        if self.pos[1] < wall_center[1]:
                            # player above wall -> move player to top of wall
                            self.pos[1] = wall.top - self.height/2
                            if self.vel[1] > -0.5:  # More lenient grounded detection
                                self.grounded = True
                                # Clamp vertical velocity when landing/grounded
                                if self.vel[1] > 0:
                                    self.vel[1] = 0
                        else:
                            # player below wall -> move player to bottom of wall
                            self.pos[1] = wall.bottom + self.height/2
                        self.vel[1] = 0  # Stop vertical velocity

                    # update hitbox after moving so next iteration uses correct position
                    self.hitbox = pygame.Rect(self.pos[0] - self.width/2, self.pos[1] - self.height/2, self.width, self.height)

            it += 1

        # Additional grounded check: if player is very close to ground and not moving up much
        if not self.grounded and abs(self.vel[1]) < 1.0:
            # Check if there's ground very close below us
            ground_check_rect = pygame.Rect(self.hitbox.left, self.hitbox.bottom, self.hitbox.width, 2)
            if ground_check_rect.collidelistall(self.border_walls):
                self.grounded = True
                self.vel[1] = 0

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 1)  # Draw hitbox for debugging
        # Try to use sprite, fallback to colored rectangle
        player_sprite = self._get_player_sprite()
        
        if player_sprite:
            # Scale sprite to match player height while maintaining aspect ratio
            target_height = int(self.height * 1.5)  # 1.5x bigger than hitbox height
            original_width = player_sprite.get_width()
            original_height = player_sprite.get_height()
            
            # Calculate width based on aspect ratio
            aspect_ratio = original_width / original_height
            sprite_width = int(target_height * aspect_ratio)
            sprite_height = target_height
            
            scaled_sprite = self.player_sprites.scale_sprite(player_sprite, sprite_width, sprite_height)
            if scaled_sprite:
                # Center the sprite on the player position
                sprite_rect = scaled_sprite.get_rect()
                sprite_rect.center = add_vecs(self.pos, [0,-10])  # Slight vertical offset
                screen.blit(scaled_sprite, sprite_rect)
            else:
                # Fallback to colored rectangle
                self._draw_fallback_rectangle(screen)
        else:
            # Fallback to colored rectangle
            self._draw_fallback_rectangle(screen)
    
    def _draw_fallback_rectangle(self, screen):
        """Fallback drawing method using colored rectangles"""
        if self.collide:
            color = (50, 200, 50)
        else:
            color = (200, 50, 50)
        pygame.draw.rect(screen, color, self.hitbox)
    
    def _preload_animations(self):
        """Preload specific animation states from individual sprite files"""
        if not self.player_sprites.sprites_loaded:
            return
            
        self.animations = {
            "idle": self.player_sprites.get_animation_frames("idle"),
            "run": self.player_sprites.get_animation_frames("run"),
            "jump": self.player_sprites.get_animation_frames("jump"),
            "hurt": self.player_sprites.get_animation_frames("hurt"),
            "death": self.player_sprites.get_animation_frames("death")
        }
        
        # Use walk as fallback for run if run doesn't exist
        if not self.animations["run"] and "walk" in self.player_sprites.animation_frames:
            self.animations["run"] = self.player_sprites.get_animation_frames("walk")
        
        print(f"Preloaded animations for '{self.name}':")
        for anim_name, frames in self.animations.items():
            print(f"  {anim_name}: {len(frames)} frames")

    def _get_player_sprite(self):
        """Determine which sprite to use based on player state"""
        if not self.player_sprites.sprites_loaded or not hasattr(self, 'animations'):
            return None
        
        # Update current state based on player conditions (simplified)
        if self.current_state == "hurt" or self.current_state == "death":
            # Keep current state until animation completes
            pass
        elif not self.grounded:
            self.current_state = "jump"
        elif abs(self.vel[0]) > 1:
            self.current_state = "run"  
        else:
            self.current_state = "idle"
        
        # Get current animation frames
        current_animation = self.animations.get(self.current_state, [])
        if not current_animation:
            # Fallback to idle if current state has no frames
            current_animation = self.animations.get("idle", [])
            if not current_animation:
                return None
        
        # Calculate frame index based on animation speed
        animation_speed = 8  # Frames per sprite frame
        frame_index = (self.current_frame // animation_speed) % len(current_animation)
        sprite = current_animation[frame_index]
        
        # Flip sprite if facing left
        if sprite and not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
            
        return sprite
    
    def set_state(self, new_state):
        """Manually set player animation state (for hurt, death, etc.)"""
        if new_state in ["idle", "run", "jump", "hurt", "death"]:
            self.current_state = new_state
            self.current_frame = 0  # Reset animation