import pygame

class Ocean:
    def __init__(self, width, height, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height
        self.width = width
        self.height = height
        self.color = (0, 0, 255)  # Blue color for the ocean

    def draw(self, screen, ship_x=0, ship_y=0):
        screen.fill(self.color)  # Fill the screen with the ocean color

        # Grid lines that move exactly with the player
        grid_size = 40
        x_offset = int(ship_x) % grid_size
        y_offset = int(ship_y) % grid_size

        for i in range(-grid_size, self.width + grid_size, grid_size):
            pygame.draw.line(screen, (30, 60, 120), (i - x_offset, 0), (i - x_offset, self.height), 1)
        for j in range(-grid_size, self.height + grid_size, grid_size):
            pygame.draw.line(screen, (30, 60, 120), (0, j - y_offset), (self.width, j - y_offset), 1)