import pygame
import math
import random
from ship import Ship
from plunder import Plunder
from cannonball import Cannonball

class NpcShip(Ship):
    def __init__(self, x, y, width=20, height=40, captain_name="Captain", ship_name="NPC Ship", player_ship=None):
        super().__init__(x, y, width, height)
        self.color = (100, 100, 100)
        self.target_angle = random.uniform(0, 360)
        self.target_sail = random.uniform(0.3, 1.0)
        self.change_timer = 0
        self.captain_name = captain_name
        self.ship_name = ship_name
        #print(player_ship)
        self.player_ship = player_ship

        # Weapons
        self.cannonballs = []
        self.cannon_reload = 0

    def drop_plunder(self):
        return Plunder(self.x, self.y, random.randint(10, 50))

    def update(self, islands=None, dt=1/60, player_ship=None):
        # Change direction and sail height every 2-5 seconds
        self.change_timer -= dt * 60
        if self.change_timer <= 0:
            self.target_angle = random.uniform(0, 360)
            self.target_sail = random.uniform(0.3, 1.0)
            self.change_timer = random.randint(10*60, 20*60)  # 2-5 seconds at 60fps

        # Smoothly adjust sail height
        if self.sail_height < self.target_sail:
            self.sail_height = min(self.sail_height + 0.0005 * dt * 60, self.target_sail)
        elif self.sail_height > self.target_sail:
            self.sail_height = max(self.sail_height - 0.0005 * dt * 60, self.target_sail)

        # Smoothly turn toward target angle
        angle_diff = (self.target_angle - self.angle + 180) % 360 - 180
        if abs(angle_diff) > 1:
            turn = self.turn_speed * dt * 60 if angle_diff > 0 else -self.turn_speed * dt * 60
            self.angle += turn
        else:
            self.angle = self.target_angle

        # Accelerate based on sail height (same as player)
        if self.sail_height > 0:
            #self.speed = min(self.speed + self.base_acceleration * self.sail_height * dt * 60, self.max_speed * self.sail_height)
            self.speed = min(self.speed + self.base_acceleration * self.sail_height * dt * 60, self.max_speed * self.sail_height)
        else:
            if self.speed > 0:
                self.speed = max(self.speed - self.base_acceleration / 2 * dt * 60, 0)
            elif self.speed < 0:
                self.speed = min(self.speed + self.base_acceleration / 2 * dt * 60, 0)

        # Update position
        rad = math.radians(self.angle)
        next_x = self.x + -self.speed * math.sin(rad) * dt * 60
        next_y = self.y + -self.speed * math.cos(rad) * dt * 60

        if islands is None or not any(
            island.contains_point(next_x, next_y) for island in islands
        ):
            self.x = next_x
            self.y = next_y
        else:
            self.speed = 0  # Stop if would collide

        # Fire cannonballs at player if in range
        self.fire_cannon(player_ship)

        # Update cannonballs
        self.update_cannonballs()

    def fire_cannon(self, player_ship):
        if player_ship is None:
            return
        
        # Reload timer
        if (self.cannon_reload > 0):
            self.cannon_reload -= 1
            return

        if self.cannon_reload <= 0:
            # Check if player is in range
            distance_to_player = math.sqrt((self.x - player_ship.x)**2 + (self.y - player_ship.y)**2)
            if distance_to_player < 500:  # Example range
                # Fire cannonballs
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

                self.cannon_reload = 60  # 1 second at 60fps

    def update_cannonballs(self):
        for ball in self.cannonballs:
            ball.update()
        # Remove cannonballs that are off screen or not alive
        self.cannonballs = [b for b in self.cannonballs if b.alive]

    def draw_cannonballs(self, screen, camera_offset_x=0, camera_offset_y=0):
        for ball in self.cannonballs:
            ball.draw(screen, camera_offset_x, camera_offset_y)

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        cx = self.x - camera_offset_x
        cy = self.y - camera_offset_y

        w = self.width
        h = self.height * 1.4  # Make the ship longer

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
        pygame.draw.polygon(screen, (100, 100, 100), [bow, stern_right, stern, stern_left])  # Gray for NPCs

        # Optional: draw a mast
        mast_top = (
            cx + math.sin(angle_rad) * h // 4,
            cy - math.cos(angle_rad) * h // 4
        )
        mast_bottom = (
            cx - math.sin(angle_rad) * h // 4,
            cy + math.cos(angle_rad) * h // 4
        )
        pygame.draw.line(screen, (180, 180, 180), mast_bottom, mast_top, 3)

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
            pygame.draw.polygon(screen, (220, 220, 220), [sail_base_left, sail_base_right, sail_tip])

        # Debug center
        #pygame.draw.circle(screen, (255, 0, 0), (int(cx), int(cy)), 3)

