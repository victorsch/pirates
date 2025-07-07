import pygame
import math

class Cannonball:
    def __init__(self, x, y, angle, speed=5, parent=None, max_range=250):
        self.x = x
        self.y = y
        self.start_x = x  # Track starting position
        self.start_y = y
        self.angle = angle
        self.speed = speed
        self.radius = 4
        self.alive = True
        self.parent = parent
        self.max_range = max_range  # Maximum distance the cannonball can travel

    def update(self): 
        rad = math.radians(self.angle)
        self.x += -self.speed * math.sin(rad)
        self.y += -self.speed * math.cos(rad)
        # Check range
        dx = self.x - self.start_x
        dy = self.y - self.start_y
        if math.hypot(dx, dy) > self.max_range:
            self.alive = False

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        pygame.draw.circle(
            screen, (30, 30, 30),
            (int(self.x - camera_offset_x), int(self.y - camera_offset_y)),
            self.radius
        )

    def collides_with_ship(self, ship):
        if (ship != self.parent and not ship.sunk):
            ship_rect = pygame.Rect(
                ship.x - ship.width // 2,
                ship.y - ship.height // 2,
                ship.width,
                ship.height
            )
            return ship_rect.collidepoint(self.x, self.y)