import pygame, random, math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, SHIP_COLOR, OCEAN_COLOR
from ship import Ship
from ocean import Ocean
from island import Island
from npc_ship import NpcShip
from port_menu import PortMenu
from tab_menu import TabMenu
import utility

# World state
active_menu = None

def is_near_port(ship, islands, interaction_radius=120):
    ship_center = pygame.Vector2(ship.x, ship.y)
    for island in islands:
        if getattr(island, "has_port", False):
            island_center = pygame.Vector2(island.x + island.width // 2, island.y + island.height // 2)
            if ship_center.distance_to(island_center) < interaction_radius:
                return True
    return False

def undock_ship(ship, island, distance=40):
    ship_center = pygame.Vector2(ship.x, ship.y)
    island_center = pygame.Vector2(island.x + island.width // 2, island.y + island.height // 2)
    direction = (ship_center - island_center)
    if direction.length() == 0:
        direction = pygame.Vector2(1, 0)  # Arbitrary direction if exactly overlapping
    direction = direction.normalize()
    ship.x += direction.x * distance
    ship.y += direction.y * distance

#at_port = nearest_port and is_near_port(ship, nearest_port)
def handle_menus(ship, port_menu, tab_menu, islands, screen, font):
    global active_menu

    # Check if player is at a port
    at_port = is_near_port(ship, islands)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "quit"
        elif event.type == pygame.KEYDOWN:
            if active_menu is None:
                if event.key == pygame.K_TAB:
                    active_menu = "tab"
                elif at_port and event.key == pygame.K_f:
                    print("Opening port menu...")
                    active_menu = "port"
                    port_menu.open()
            elif active_menu == "tab":
                result = tab_menu.handle_event(event)
                if event.key == pygame.K_TAB or event.key == pygame.K_ESCAPE:
                    active_menu = None
            elif active_menu == "port":
                result = port_menu.handle_event(event)
                if result == "Leave Port" or event.key == pygame.K_ESCAPE:
                    port_menu.close()
                    active_menu = None
            # Handle other port menu actions here

    
    return None  # Continue normal gameplay

def main():
    pygame.init()

    

    # World info
    MAP_WIDTH = 20000
    MAP_HEIGHT = 20000
    island_count = 100

    # Set up the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Open World Pirate Game")
    clock = pygame.time.Clock()
    #dt = clock.tick(60) / 1000.0  # 60 FPS cap, dt in seconds
    font = pygame.font.SysFont(None, 24)

    SMOOTHING = 0.1 # For movement - Lower = more lag, Higher = snappier

    # Notifications at top of screen
    notifications = []  # List of (message, time_to_live)
    notification_duration = 20.0  # seconds

    # Player ship stats
    player_plunder = 0
    player_crew = 20

    # Create instances of Ship and Ocean
    ocean = Ocean(SCREEN_WIDTH,SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT)
    ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 20, 40)


    # Create islands, avoiding the player ship's spawn area
    islands = []
    while len(islands) < island_count:
        ix = random.randint(-MAP_WIDTH, MAP_WIDTH)
        iy = random.randint(-MAP_HEIGHT, MAP_HEIGHT)
        island = Island(ix, iy)
        # Check overlap with player ship
        ship_rect = pygame.Rect(
            ship.x - ship.width // 2,
            ship.y - ship.height // 2,
            ship.width,
            ship.height
        )
        island_rect = pygame.Rect(island.x, island.y, island.width, island.height)
        if not island_rect.colliderect(ship_rect):
            islands.append(island)

    # spawn port island just to left of player spawn
    port_island = Island(ship.x - 200, ship.y, has_port=True)
    islands.append(port_island)

    # Create NPC ships, avoiding islands
    npc_ships = []
    while len(npc_ships) < 15:
        nx = random.randint(-500, 1500)
        ny = random.randint(-500, 1500)
        npc = NpcShip(nx, ny, captain_name=utility.generate_captain_name(), ship_name=utility.generate_ship_name())
        npc_rect = pygame.Rect(
            npc.x - npc.width // 2,
            npc.y - npc.height // 2,
            npc.width,
            npc.height
        )
        # Ensure NPC does not spawn on any island
        if not any(pygame.Rect(island.x, island.y, island.width, island.height).colliderect(npc_rect) for island in islands):
            npc_ships.append(npc)


    # Menus
    port_menu = PortMenu()
    tab_menu = TabMenu(ship)

    # Main game loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        # Handle menus
        menu_state = handle_menus(ship, port_menu, tab_menu, islands, screen, font)
        if menu_state == "quit":
            running = False
            break
        elif menu_state == "menu":
            continue  # Skip the rest of the loop this frame

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Gameplay logic

        # Display logic
        
        # Camera offset so ship is always centered
        camera_offset_x = ship.x - SCREEN_WIDTH // 2
        camera_offset_y = ship.y - SCREEN_HEIGHT // 2
        
        # Fill the background with ocean color
        ocean.draw(screen, ship.x, ship.y)
        
        # Draw the ship
        ship.draw(screen, camera_offset_x, camera_offset_y)

         # Draw islands
        for island in islands:
            island.draw(screen, camera_offset_x, camera_offset_y)

        
        # In your game loop:
        npc_ships = [npc for npc in npc_ships if not npc.sunk] # Remove sunk NPC ships
        for npc in npc_ships:
            npc.update(islands, dt=dt)
            npc.draw(screen, camera_offset_x, camera_offset_y)
            if not npc.sunk:
                npc.update(islands)
                for ball in ship.cannonballs:
                    if ball.alive and ball.collides_with_ship(npc):
                        npc.sunk = True
                        ball.alive = False
                        msg = f"Sank {npc.captain_name}'s ship {npc.ship_name}!"
                        notifications.append([msg, notification_duration])
                        player_plunder += random.randint(10, 50)  # Example plunder
                        player_crew += random.randint(1, 5) 
                npc.draw(screen, camera_offset_x, camera_offset_y)
            for ball in npc.cannonballs:
                if ball.alive and ball.collides_with_ship(ship):
                    # Handle player hit (e.g., reduce health, sink, etc.)
                    ball.alive = False
        


        # Player
        next_x = ship.x
        next_y = ship.y
        rad = math.radians(ship.angle)
        next_x += -ship.speed * math.sin(rad)
        next_y += -ship.speed * math.cos(rad)

        # Each frame:
        ship.update_cannonballs()
        ship.draw_cannonballs(screen, camera_offset_x, camera_offset_y)

        if not ship.collides_with_island(next_x, next_y, islands, ship.width, ship.height):
            ship.x = next_x
            ship.y = next_y
        else:
            ship.speed = 0  # Stop the ship if it would collide


        if active_menu is None:
            ship.update(pygame.key.get_pressed(), dt)


        # Update notifications
        for note in notifications:
            note[1] -= dt
        notifications[:] = [n for n in notifications if n[1] > 0]

        # Draw overlay
        
        overlay_lines = [
            f"Plunder: {player_plunder}",
            f"Crew: {player_crew}"
        ]
        for i, line in enumerate(overlay_lines):
            text = font.render(line, True, (255, 255, 0))
            screen.blit(text, (10, 10 + i * 22))

        # Draw notifications
        for i, note in enumerate(notifications):
            text = font.render(note[0], True, (255, 200, 200))
            screen.blit(text, (10, 60 + i * 22))

        # Interact prompt
        at_port = is_near_port(ship, islands)
        if at_port and not port_menu.active:
            prompt_text = font.render("Press F to interact with port", True, (255, 255, 255))
            screen.blit(prompt_text, (10, SCREEN_HEIGHT - 40))


        # Draw arrow to nearest island (for debugging)
        if islands:
            # Find nearest island
            ship_center = pygame.Vector2(ship.x, ship.y)
            nearest_island = min(islands, key=lambda isl: ship_center.distance_to((isl.x + isl.width // 2, isl.y + isl.height // 2)))
            island_center = pygame.Vector2(nearest_island.x + nearest_island.width // 2, nearest_island.y + nearest_island.height // 2)

            # Calculate positions relative to camera
            start_pos = (int(ship.x - camera_offset_x), int(ship.y - camera_offset_y))
            end_pos = (int(island_center.x - camera_offset_x), int(island_center.y - camera_offset_y))

            

            # Draw arrowhead
            direction = (island_center - ship_center).normalize()
            arrow_length = 20
            left = direction.rotate(150) * arrow_length
            right = direction.rotate(-150) * arrow_length
            arrow_tip = pygame.Vector2(end_pos)

            # Draw main line
            #pygame.draw.line(screen, (0, 255, 0), start_pos, end_pos, 3)
            #pygame.draw.line(screen, (0, 255, 0), arrow_tip, arrow_tip - left, 3)
            #pygame.draw.line(screen, (0, 255, 0), arrow_tip, arrow_tip - right, 3)
        
        if active_menu == "tab":
            # Draw your tab menu overlay here
            tab_menu.draw(screen, font)
        elif active_menu == "port":
            port_menu.draw(screen, font)

        # Update the display
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()