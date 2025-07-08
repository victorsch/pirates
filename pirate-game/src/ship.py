import pygame
import math
from cannonball import Cannonball

class Ship:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # Attributes
        self.name = "Player Ship"

        # Status
        self.hull_health = 100
        self.sunk = False  # Whether the ship is sunk

        # Inventory
        self.inventory = {
            "cannonballs": 100,
        }

        # Movement
        self.angle = 0  # Ship's facing direction in degrees
        self.speed = 0
        self.max_speed = 1
        self.base_acceleration = .01
        self.min_turn_speed = .5
        self.turn_speed = 1
        self.sail_height = 0.0

        # Weapons
        self.equipped_weapon = "cannonballs"
        self.cannonballs = []
        self.cannon_reload = 0

        # Debug
        #self._last_broadside_points = []

    def update(self, keys, dt):
        # Adjust sail height
        if keys[pygame.K_UP]:
            self.sail_height = min(self.sail_height + 0.05, 1.0)
        if keys[pygame.K_DOWN]:
            self.sail_height = max(self.sail_height - 0.05, 0.0)


        # Old movement logic
        # Accelerate based on sail height
        # if self.sail_height > 0:
        #     print(self.speed, self.base_acceleration, self.sail_height)
        #     self.speed = min(self.speed + self.base_acceleration * self.sail_height * dt * 60, self.max_speed * self.sail_height)
        # else:
        #     # Gradual stop (friction)
        #     if self.speed > 0:
        #         self.speed = max(self.speed - self.base_acceleration * dt * 60, 0)
        #     elif self.speed < 0:
        #         self.speed = min(self.speed + self.base_acceleration * dt * 60, 0)

        ## New movement logic
        #print(self.speed, self.base_acceleration, self.sail_height)
        target_speed = self.max_speed * self.sail_height
        if self.speed < target_speed:
            self.speed = min(self.speed + self.base_acceleration * dt * 60, target_speed)
        elif self.speed > target_speed:
            self.speed = max(self.speed - self.base_acceleration * dt * 60, target_speed)

        # Adjust turning speed based on current speed
        turn_factor = max(0.5, 1 - (self.speed / self.max_speed))

        # Turning (only when moving)
        if self.speed != 0:
            if keys[pygame.K_LEFT]:
                self.angle += self.turn_speed * turn_factor * dt * 60
            if keys[pygame.K_RIGHT]:
                self.angle -= self.turn_speed * turn_factor * dt * 60
        else:
            if keys[pygame.K_LEFT]:
                self.angle += self.min_turn_speed * dt * 60
            if keys[pygame.K_RIGHT]:
                self.angle -= self.min_turn_speed * dt * 60

        # Update position based on angle and speed
        rad = math.radians(self.angle)
        self.x += -self.speed * math.sin(rad) * dt * 60
        self.y += -self.speed * math.cos(rad) * dt * 60

        # Fire cannon
        if keys[pygame.K_SPACE]:
            self.fire_cannon()

        # Cannon reload timer
        if self.cannon_reload > 0:
            self.cannon_reload -= dt * 60

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        # Calculate ship center
        cx = self.x - camera_offset_x
        cy = self.y - camera_offset_y

        # Ship dimensions
        w = self.width
        h = self.height * 1.4  # Make the ship longer

        # Calculate points for a more "ship-like" polygon
        angle_rad = math.radians(-self.angle)
        bow = (
            cx + math.sin(angle_rad) * h // 2,
            cy - math.cos(angle_rad) * h // 2
        )
        stern_left = (
            cx + math.sin(angle_rad + math.pi * 0.75) * w // 2,
            cy - math.cos(angle_rad + math.pi * 0.75) * w // 2
        )
        stern_right = (
            cx + math.sin(angle_rad - math.pi * 0.75) * w // 2,
            cy - math.cos(angle_rad - math.pi * 0.75) * w // 2
        )
        stern = (
            cx - math.sin(angle_rad) * h // 2 * 0.6,
            cy + math.cos(angle_rad) * h // 2 * 0.6
        )

        # Draw the ship as a polygon (elongated hull)
        pygame.draw.polygon(screen, (139, 69, 19), [bow, stern_right, stern, stern_left])

        # Optional: draw a mast
        mast_top = (
            cx + math.sin(angle_rad) * h // 4,
            cy - math.cos(angle_rad) * h // 4
        )
        mast_bottom = (
            cx - math.sin(angle_rad) * h // 4,
            cy + math.cos(angle_rad) * h // 4
        )
        pygame.draw.line(screen, (220, 220, 220), mast_bottom, mast_top, 3)

        # Draw the sail (visual indicator of sail_height)
        sail_length = (h // 2) * self.sail_height
        if self.sail_height > 0:
            sail_base_left = (
                mast_top[0] - math.cos(angle_rad) * w // 8,
                mast_top[1] - math.sin(angle_rad) * w // 8
            )
            sail_base_right = (
                mast_top[0] + math.cos(angle_rad) * w // 8,
                mast_top[1] + math.sin(angle_rad) * w // 8
            )
            sail_tip = (
                mast_top[0] + math.sin(angle_rad) * sail_length,
                mast_top[1] - math.cos(angle_rad) * sail_length
            )
            pygame.draw.polygon(screen, (255, 255, 255), [sail_base_left, sail_base_right, sail_tip])

        # Debug center
        #pygame.draw.circle(screen, (255, 0, 0), (int(cx), int(cy)), 3)


    def collides_with_island(self, x, y, islands, ship_width, ship_height):
        for island in islands:
            island_rect = pygame.Rect(island.x, island.y, island.width, island.height)
            ship_rect = pygame.Rect(x - ship_width // 2, y - ship_height // 2, ship_width, ship_height)
            if island_rect.colliderect(ship_rect):
                # Bounce off the island
                direction = pygame.Vector2(x - island.x, y - island.y).normalize()
                self.x += direction.x * 10  # Move away by 10 units
                self.y += direction.y * 10
                return True
        return False
    
    def fire_cannon(self):
        if self.equipped_weapon:
            if self.inventory.get(self.equipped_weapon, 0) <= 0:
                print(f"Out of {self.equipped_weapon}!")
                return
            elif self.cannon_reload <= 0:
                # Use ammo
                if not self.use_ammo(self.equipped_weapon, 1):
                    print(f"Failed to use ammo for {self.equipped_weapon}!")
                    return

                # Adjust cannonball positioning to align with the ship's center and orientation
                offset = self.width // 2
                angle_rad = math.radians(self.angle)

                # Perpendicular vector (unit vector)
                perp_x = math.cos(angle_rad)
                perp_y = -math.sin(angle_rad)

                # Left broadside (port)
                lx = self.x + offset * perp_x
                ly = self.y + offset * perp_y
                self.cannonballs.append(Cannonball(lx, ly, self.angle + 90, parent=self))

                # Right broadside (starboard)
                rx = self.x - offset * perp_x
                ry = self.y - offset * perp_y
                self.cannonballs.append(Cannonball(rx, ry, self.angle - 90, parent=self))
                
                # Debug spawns
                #self._last_broadside_points = [(lx, ly), (rx, ry)]

                self.cannon_reload = 60  # 1 second at 60fps
        else:
            print("No weapon equipped!")

    def use_ammo(self, ammo_type, amount):
        if ammo_type in self.inventory:
            if self.inventory[ammo_type] >= amount:
                self.inventory[ammo_type] -= amount
                return True
            else:
                print(f"Not enough {ammo_type}!")
                return False
        else:
            print(f"{ammo_type} not found in inventory!")
            return False

    def update_cannonballs(self):
        for ball in self.cannonballs:
            ball.update()
        # Remove cannonballs that are off screen or not alive
        self.cannonballs = [b for b in self.cannonballs if b.alive]

    def draw_cannonballs(self, screen, camera_offset_x=0, camera_offset_y=0):
        for ball in self.cannonballs:
            ball.draw(screen, camera_offset_x, camera_offset_y)