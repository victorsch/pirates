import pygame
import random

class PortMenu:
    def __init__(self):
        self.active = False
        self.options = ["Buy Goods", "Sell Goods", "Leave Port"]
        self.selected_option = 0
        self.goods_cost = random.randint(30, 70)  # Dynamic cost for goods
        self.options.append("Repair Hull")  # Add repair hull option
        self.repair_cost = random.randint(50, 100)  # Dynamic cost for hull repair

    def open(self):
        self.active = True

    def close(self):
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                if self.options[self.selected_option] == "Repair Hull":
                    return "Repair Hull"
                return self.options[self.selected_option]
        return None

    def draw(self, screen, font):
        # Draw background
        menu_width, menu_height = 300, 200
        menu_x, menu_y = (screen.get_width() - menu_width) // 2, (screen.get_height() - menu_height) // 2
        pygame.draw.rect(screen, (50, 50, 50), (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, (200, 200, 200), (menu_x, menu_y, menu_width, menu_height), 2)

        # Draw options
        for i, option in enumerate(self.options):
            color = (255, 255, 255) if i == self.selected_option else (200, 200, 200)
            text = font.render(option, True, color)
            screen.blit(text, (menu_x + 20, menu_y + 20 + i * 30))

        # Display dynamic goods cost
        cost_text = font.render(f"Goods Cost: {self.goods_cost} gold", True, (255, 255, 0))
        screen.blit(cost_text, (menu_x + 20, menu_y + menu_height - 40))

        # Display repair cost
        repair_text = font.render(f"Repair Cost: {self.repair_cost} gold", True, (255, 255, 0))
        screen.blit(repair_text, (menu_x + 20, menu_y + menu_height - 70))