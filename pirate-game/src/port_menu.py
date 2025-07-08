import pygame

class PortMenu:
    def __init__(self, player_inventory, player_ship):
        self.active = False
        self.state = "main"
        self.selected = 0
        self.player_inventory = player_inventory
        self.player_ship = player_ship
        self.options = {
            "main": ["Trade", "Repair Ship", "Leave Port"],
            "trade": ["Buy Rum (10 gold)", "Sell Cargo", "Back"],
            "repair": ["Repair Hull (15 gold)", "Back"]
        }

    def open(self):
        self.active = True
        self.selected = 0
        self.state = "main"

    def close(self):
        self.active = False

    def handle_event(self, event):
        opts = self.options[self.state]
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(opts)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(opts)
            elif event.key == pygame.K_RETURN:
                choice = opts[self.selected]
                if self.state == "main":
                    if choice == "Trade":
                        self.state = "trade"
                        self.selected = 0
                    elif choice == "Repair Ship":
                        self.state = "repair"
                        self.selected = 0
                    elif choice == "Leave Port":
                        self.close()
                        return "Leave Port"
                elif self.state in ("trade", "repair"):
                    if choice == "Back":
                        self.state = "main"
                        self.selected = 0
                    else:
                        self.perform_action(choice)
            elif event.key == pygame.K_ESCAPE:
                if self.state == "main":
                    self.close()
                    return "Leave Port"
                else:
                    self.state = "main"
                    self.selected = 0

    def perform_action(self, choice):
        if self.state == "trade":
            if choice == "Buy Rum (10 gold)":
                if self.player_ship.inventory.get("gold", 0) >= 10:  # Ensure gold is sufficient
                    self.player_ship.inventory["gold"] -= 10
                    self.player_ship.inventory["goods"] = self.player_ship.inventory.get("goods", 0) + 1
                    print(f"Bought Rum! Gold: {self.player_ship.inventory['gold']}, Goods: {self.player_ship.inventory['goods']}")
                else:
                    print("Not enough gold!")
            elif choice == "Sell Cargo":
                if self.player_ship.inventory.get("goods", 0) > 0:  # Ensure goods are available
                    self.player_ship.inventory["goods"] -= 1
                    self.player_ship.inventory["gold"] += 5
                    print(f"Sold Cargo! Gold: {self.player_ship.inventory['gold']}, Goods: {self.player_ship.inventory['goods']}")
                else:
                    print("No goods to sell!")
        elif self.state == "repair":
            if choice == "Repair Hull (15 gold)":
                if self.player_ship.inventory.get("gold", 0) >= 15:  # Ensure gold is sufficient
                    self.player_ship.inventory["gold"] -= 15
                    self.player_ship.hull_health = min(self.player_ship.hull_health + 20, 100)
                    print(f"Repaired Hull! Gold: {self.player_ship.inventory['gold']}, Hull Health: {self.player_ship.hull_health}")
                else:
                    print("Not enough gold!")

    def draw(self, screen, font):
        menu_rect = pygame.Rect(100, 100, 350, 250)
        pygame.draw.rect(screen, (30, 30, 60), menu_rect)
        pygame.draw.rect(screen, (200, 200, 255), menu_rect, 2)
        title = font.render(f"Port: {self.state.capitalize()}", True, (255, 255, 255))
        screen.blit(title, (menu_rect.x + 20, menu_rect.y + 10))
        opts = self.options[self.state]
        for i, option in enumerate(opts):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = font.render(option, True, color)
            screen.blit(text, (menu_rect.x + 20, menu_rect.y + 50 + i * 40))