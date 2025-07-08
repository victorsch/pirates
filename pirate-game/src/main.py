import pygame, random, math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, SHIP_COLOR, OCEAN_COLOR
from ship import Ship
from ocean import Ocean
from island import Island
from npc_ship import NpcShip
from port_menu import PortMenu
from tab_menu import TabMenu
import utility

CHUNK_SIZE = 1000
loaded_chunks = {}  # {(chunk_x, chunk_y): {"islands": [...], "npcs": [...]}}

def get_chunk_coords(x, y):
    return int(x // CHUNK_SIZE), int(y // CHUNK_SIZE)

def generate_chunk(chunk_x, chunk_y):
    # Procedurally generate islands
    random.seed((chunk_x, chunk_y, "island"))
    islands = []
    for _ in range(random.randint(0, 2)):
        ix = chunk_x * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
        iy = chunk_y * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
        has_port = random.choice([True, False])
        name = utility.generate_island_name()
        port_name = utility.generate_port_name() if has_port else None
        islands.append(Island(ix, iy, has_port=has_port, name=name, port_name=port_name))

    # Procedurally generate NPC ships
    random.seed((chunk_x, chunk_y, "npc"))
    npcs = []
    for _ in range(random.randint(4, 8)):
        nx = chunk_x * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
        ny = chunk_y * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
        npcs.append(NpcShip(nx, ny, captain_name=utility.generate_captain_name(), ship_name=utility.generate_ship_name()))
    return {"islands": islands, "npcs": npcs}

def update_chunks(player_x, player_y):
    player_chunk = get_chunk_coords(player_x, player_y)
    # Load nearby chunks
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            chunk = (player_chunk[0] + dx, player_chunk[1] + dy)
            if chunk not in loaded_chunks:
                loaded_chunks[chunk] = generate_chunk(*chunk)
    # Optionally, unload far chunks for memory
    chunks_to_keep = set((player_chunk[0] + dx, player_chunk[1] + dy) for dx in range(-2, 3) for dy in range(-2, 3))
    for chunk in list(loaded_chunks.keys()):
        if chunk not in chunks_to_keep:
            del loaded_chunks[chunk]

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
    return None  # Continue normal gameplay

def draw_overlay(screen, font, player_inventory):
    # Draw overlay with player stats
    overlay_rect = pygame.Rect(10, 10, 200, 100)
    pygame.draw.rect(screen, (0, 0, 0), overlay_rect)
    pygame.draw.rect(screen, (255, 255, 255), overlay_rect, 2)

    # Display player inventory
    inventory_lines = [
        f"Gold: {player_inventory.get('gold', 0)}",
        f"Goods: {player_inventory.get('goods', 0)}",
        f"Crew: {player_inventory.get('crew', 0)}"
    ]
    for i, line in enumerate(inventory_lines):
        text = font.render(line, True, (255, 255, 255))
        screen.blit(text, (overlay_rect.x + 10, overlay_rect.y + 10 + i * 30))

def draw_notifications(screen, font, notifications):
    # Draw notifications below the overlay
    notification_y = 120  # Position below the overlay
    for message, ttl in notifications:
        text = font.render(message, True, (255, 255, 255))
        screen.blit(text, (10, notification_y))
        notification_y += 30

def main():
    pygame.init()

    # World info
    MAP_WIDTH = 20000
    MAP_HEIGHT = 20000

    # Set up the game window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Open World Pirate Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    SMOOTHING = 0.1 # For movement - Lower = more lag, Higher = snappier

    # Notifications at top of screen
    notifications = []  # List of (message, time_to_live)
    notification_duration = 3.0  # seconds

    # Player ship stats
    player_plunder = 0
    player_crew = 20
    player_inventory = {
        "gold": 0,
        "goods": 0,
        "crew": player_crew
    }

    # Create instances of Ship and Ocean
    ocean = Ocean(SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT)
    ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 20, 40)

    # Menus
    port_menu = PortMenu()
    tab_menu = TabMenu(ship)

    # List to store plunder objects
    plunder_objects = []

    # Main game loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        # Update procedural chunks based on player position
        update_chunks(ship.x, ship.y)

        # Gather all islands and npcs from loaded chunks
        islands = []
        npc_ships = []
        for chunk in loaded_chunks.values():
            islands.extend(chunk["islands"])
            npc_ships.extend(chunk["npcs"])

        # Handle menus
        menu_state = handle_menus(ship, port_menu, tab_menu, islands, screen, font)
        if menu_state == "quit":
            running = False
            break
        elif menu_state == "menu":
            continue  # Skip the rest of the loop this frame

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

        # Remove sunk NPC ships and handle plunder
        npc_ships = [npc for npc in npc_ships if not npc.sunk]
        for npc in npc_ships:
            npc.update(islands, dt=dt)
            npc.draw(screen, camera_offset_x, camera_offset_y)

        # Draw and handle plunder
        for plunder in plunder_objects:
            plunder.draw(screen, camera_offset_x, camera_offset_y)
            plunder.check_collision(ship)

        # Player movement and logic
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

        # Check cannonball collisions with NPC ships
        for npc in npc_ships:
            for ball in ship.cannonballs:
                if ball.alive and ball.collides_with_ship(npc):
                    npc.sunk = True
                    ball.alive = False
                    msg = f"Sank {npc.captain_name}'s ship {npc.ship_name}!"
                    notifications.append([msg, notification_duration])
                    plunder_objects.append(npc.drop_plunder())

        # Update player inventory after collecting plunder
        player_inventory['gold'] = ship.inventory.get('gold', 0)
        player_inventory['goods'] = ship.inventory.get('goods', 0)
        player_inventory['crew'] = ship.inventory.get('crew', 0)

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
        notification_y = 120  # Position below the overlay
        for i, note in enumerate(notifications):
            text = font.render(note[0], True, (255, 200, 200))
            screen.blit(text, (10, notification_y + i * 22))

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
            tab_menu.draw(screen, font)
        elif active_menu == "port":
            port_menu.draw(screen, font)

        draw_overlay(screen, font, player_inventory)
        draw_notifications(screen, font, notifications)

        # Update the display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()