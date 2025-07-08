import pygame
import random

class Island:
    def __init__(self, x, y, has_port=None, name=None, port_name=None):
        self.x = x
        self.y = y
        self.width = random.randint(60, 150)
        self.height = random.randint(60, 150)
        self.has_port = has_port
        self.name = name
        self.port_name = port_name
        self.font = pygame.font.SysFont(None, 20)
        if self.name:
            self.name_surface = self.font.render(self.name, True, (0, 0, 0))
        else:
            self.name_surface = None
        if self.has_port and self.port_name:
            self.port_surface = self.font.render(self.port_name, True, (139, 69, 19))
        else:
            self.port_surface = None

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

        # Draw island name if visible
        if self.name_surface:
            screen.blit(self.name_surface, (self.x - camera_offset_x, self.y - camera_offset_y - 20))
        # Draw port name if applicable and visible
        if self.port_surface:
            screen.blit(self.port_surface, (self.x - camera_offset_x, self.y - camera_offset_y + self.height + 5))

    def contains_point(self, x, y):
        return (self.x <= x <= self.x + self.width) and (self.y <= y <= self.y + self.height)