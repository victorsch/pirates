import pygame

class TabMenu:
    def __init__(self, ship):
        self.active = False
        self.selected = 0
        self.sections = ["Inventory", "Loadout", "Coordinates", "Back"]
        self.ship = ship  # Reference to the player's ship

    def open(self):
        self.active = True
        self.selected = 0

    def close(self):
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.sections)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.sections)
            elif event.key == pygame.K_RETURN:
                choice = self.sections[self.selected]
                if choice == "Back":
                    self.close()
                    return "Back"
            elif event.key == pygame.K_ESCAPE:
                self.close()
                return "Back"
        return None

    def draw(self, screen, font):
        menu_rect = pygame.Rect(100, 100, 400, 300)
        pygame.draw.rect(screen, (20, 20, 40), menu_rect)
        pygame.draw.rect(screen, (200, 200, 255), menu_rect, 2)
        # Title
        title = font.render("Ship Menu", True, (255, 255, 255))
        screen.blit(title, (menu_rect.x + 20, menu_rect.y + 10))
        # Sections
        for i, section in enumerate(self.sections):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = font.render(section, True, color)
            screen.blit(text, (menu_rect.x + 20, menu_rect.y + 50 + i * 40))

        # Show details for selected section
        detail_y = menu_rect.y + 50 + len(self.sections) * 40 + 10
        if self.sections[self.selected] == "Inventory":
            inv = getattr(self.ship, "inventory", {"Rum": 0, "Cargo": 0})
            y = detail_y
            for k, v in inv.items():
                text = font.render(f"{k}: {v}", True, (180, 220, 255))
                screen.blit(text, (menu_rect.x + 40, y))
                y += 28
        elif self.sections[self.selected] == "Loadout":
            # Example: show number of cannonballs
            text = font.render(f"Cannonballs: {len(getattr(self.ship, 'cannonballs', []))}", True, (180, 220, 255))
            screen.blit(text, (menu_rect.x + 40, detail_y))
        elif self.sections[self.selected] == "Coordinates":
            coords = f"({int(self.ship.x)}, {int(self.ship.y)})"
            text = font.render(f"Coordinates: {coords}", True, (180, 220, 255))
            screen.blit(text, (menu_rect.x + 40, detail_y))

        # Display player inventory
        menu_x, menu_y = 50, 50
        player_inventory = getattr(self.ship, "inventory", {})
        inventory_lines = [
            f"Gold: {player_inventory.get('gold', 0)}",
            f"Goods: {player_inventory.get('goods', 0)}",
            f"Crew: {player_inventory.get('crew', 0)}"
        ]
        for i, line in enumerate(inventory_lines):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (menu_x, menu_y + i * 30))