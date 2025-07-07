import pygame
import random

class Island:
    def __init__(self, x, y, has_port=None):
        self.x = x
        self.y = y
        self.width = random.randint(60, 150)
        self.height = random.randint(60, 150)
        self.has_port = has_port
        self.settlement = random.choice([None, "Village", "Town", "City"])
        self.population = random.randint(0, 5000) if self.settlement else 0
        self.law_status = random.choice(["Lawless", "Orderly", "Pirate Haven"])
        self.ownership = random.choice(["None", "Empire", "Pirates", "Merchants"])

    def draw(self, screen, camera_offset_x, camera_offset_y):
        rect = pygame.Rect(
            self.x - camera_offset_x,
            self.y - camera_offset_y,
            self.width,
            self.height
        )
        pygame.draw.rect(screen, (237, 201, 175), rect)
        # Optionally, draw a port/settlement marker
        if self.has_port:
            pygame.draw.circle(screen, (139, 69, 19), rect.center, 8)

    def contains_point(self, x, y):
        return (self.x <= x <= self.x + self.width) and (self.y <= y <= self.y + self.height)