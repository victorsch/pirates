import pygame

class PortMenu:
    def __init__(self):
        self.active = False
        self.state = "main"
        self.options = ["Trade", "Recruit Crew", "Repair Ship", "Leave Port"]
        self.selected = 0
        self.options = {
            "main": ["Trade", "Recruit Crew", "Repair Ship", "Leave Port"],
            "trade": ["Buy Rum (10 gold)", "Sell Cargo", "Back"],
            "recruit": ["Hire 5 Crew (20 gold)", "Back"],
            "repair": ["Repair Hull (15 gold)", "Back"]
        }
    def open(self):
        self.active = True
        self.selected = 0

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
                # Handle submenu navigation
                if self.state == "main":
                    if choice == "Trade":
                        self.state = "trade"
                        self.selected = 0
                    elif choice == "Recruit Crew":
                        self.state = "recruit"
                        self.selected = 0
                    elif choice == "Repair Ship":
                        self.state = "repair"
                        self.selected = 0
                    elif choice == "Leave Port":
                        self.close()
                        return "Leave Port"
                elif self.state in ("trade", "recruit", "repair"):
                    if choice == "Back":
                        self.state = "main"
                        self.selected = 0
                    else:
                        return (self.state, choice)
            elif event.key == pygame.K_ESCAPE:
                if self.state == "main":
                    self.close()
                    return "Leave Port"
                else:
                    self.state = "main"
                    self.selected = 0
        return None


    def draw(self, screen, font):
        menu_rect = pygame.Rect(100, 100, 350, 250)
        pygame.draw.rect(screen, (30, 30, 60), menu_rect)
        pygame.draw.rect(screen, (200, 200, 255), menu_rect, 2)
        # Title
        title = font.render(f"Port: {self.state.capitalize()}", True, (255, 255, 255))
        screen.blit(title, (menu_rect.x + 20, menu_rect.y + 10))
        # Options
        opts = self.options[self.state]
        for i, option in enumerate(opts):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = font.render(option, True, color)
            screen.blit(text, (menu_rect.x + 20, menu_rect.y + 50 + i * 40))