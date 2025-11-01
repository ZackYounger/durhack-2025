import pygame

from helpers import add_vecs, mult_vec_float

class Player:
    def __init__(self, block_width, border_walls):
        self.jump_strength = 15
        self.dash_strength = 20
        self.dashCooldown = 60
        self.lastDashTick = 0

        self.acc_scaling = 1.5
        self.horizontal_vel_drag = 0.7
        self.vertical_vel_drag = 0.95
        
        self.width = 20
        self.height = 30

        self.grounded = False

        self.block_width = block_width
        self.border_walls = border_walls

        self.pos = [50, 50]
        self.vel = [0, 0]
        self.acc = [0, 0]

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

        self.vel = add_vecs(self.acc, self.vel)
        self.vel[0] *= self.horizontal_vel_drag
        self.vel[1] *= self.vertical_vel_drag

        self.pos = add_vecs(self.vel, self.pos)



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

                # only resolve if overlapping on the perpendicular axis
                if abs(distance[perp]) < (self.block_width / 2 + player_half_perp):
                    # place the player's edge flush with the wall edge depending on side
                    if dr == 1:
                        # vertical resolution (y axis)
                        if self.pos[1] < wall_center[1]:
                            # player above wall -> set bottom = wall.top
                            self.pos[1] = wall.top - player_half_dr
                            self.grounded = True
                        else:
                            # player below wall -> set top = wall.bottom
                            self.pos[1] = wall.bottom + player_half_dr
                    else:
                        # horizontal resolution (x axis)
                        if self.pos[0] < wall_center[0]:
                            # player left of wall -> set right = wall.left
                            self.pos[0] = wall.left - player_half_dr
                        else:
                            # player right of wall -> set left = wall.right
                            self.pos[0] = wall.right + player_half_dr

                    # stop velocity along the resolved axis to avoid re-penetration
                    self.vel[dr] = 0

                    # update hitbox after moving so next iteration uses correct position
                    self.hitbox = pygame.Rect(self.pos[0] - self.width/2, self.pos[1] - self.height/2, self.width, self.height)

            it += 1

        

    def draw(self, screen):
        if self.collide:
            color = (50, 200, 50)
        else:
            color = (200, 50, 50)
        pygame.draw.rect(screen, color, self.hitbox)