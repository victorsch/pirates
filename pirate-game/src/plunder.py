import pygame

class Plunder:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value

    def draw(self, screen, camera_offset_x, camera_offset_y):
        pygame.draw.circle(
            screen, (255, 215, 0),  # Gold color
            (int(self.x - camera_offset_x), int(self.y - camera_offset_y)),
            10  # Radius of the plunder circle
        )

    def check_collision(self, ship):
        ship_rect = pygame.Rect(
            ship.x - ship.width // 2,
            ship.y - ship.height // 2,
            ship.width,
            ship.height
        )
        return ship_rect.collidepoint(self.x, self.y)
