import pygame
import random

class Plunder:
    def __init__(self, x, y, gold=0, goods=0, crew=0):
        self.x = x
        self.y = y
        self.gold = gold
        self.goods = goods
        self.crew = crew
        self.radius = 10  # Size of the plunder marker
        self.collected = False

    def draw(self, screen, camera_offset_x=0, camera_offset_y=0):
        if not self.collected:
            pygame.draw.circle(
                screen, (255, 215, 0),  # Gold color
                (int(self.x - camera_offset_x), int(self.y - camera_offset_y)),
                self.radius
            )

    def check_collision(self, ship):
        if not self.collected:
            ship_rect = pygame.Rect(
                ship.x - ship.width // 2,
                ship.y - ship.height // 2,
                ship.width,
                ship.height
            )
            plunder_rect = pygame.Rect(
                self.x - self.radius,
                self.y - self.radius,
                self.radius * 2,
                self.radius * 2
            )
            if ship_rect.colliderect(plunder_rect):
                self.collected = True
                ship.inventory['gold'] = ship.inventory.get('gold', 0) + self.gold
                ship.inventory['goods'] = ship.inventory.get('goods', 0) + self.goods
                ship.inventory['crew'] = ship.inventory.get('crew', 0) + self.crew