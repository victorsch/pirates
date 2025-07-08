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

def generate_chunk(chunk_x, chunk_y, player_ship=None):
    # Procedurally generate islands
    random.seed((chunk_x, chunk_y, "island"))
    islands = []
    for _ in range(random.randint(2, 4)):
        ix = chunk_x * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
        iy = chunk_y * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
        has_port = random.choice([True, False])
        island_name = utility.generate_island_name()
        port_name = utility.generate_port_name() if has_port else None
        islands.append(Island(ix, iy, has_port=has_port, name=island_name, port_name=port_name))
    # Procedurally generate NPC ships
    random.seed((chunk_x, chunk_y, "npc"))
    npcs = []
    for _ in range(random.randint(2, 4)):
        nx = chunk_x * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
        ny = chunk_y * CHUNK_SIZE + random.randint(0, CHUNK_SIZE)
        npcs.append(NpcShip(nx, ny, captain_name=utility.generate_captain_name(), ship_name=utility.generate_ship_name(), player_ship=player_ship))
    return {"islands": islands, "npcs": npcs}

def update_chunks(player_x, player_y, player_ship=None):
    player_chunk = get_chunk_coords(player_x, player_y)
    # Load nearby chunks
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            chunk = (player_chunk[0] + dx, player_chunk[1] + dy)
            if chunk not in loaded_chunks:
                loaded_chunks[chunk] = generate_chunk(*chunk, player_ship=player_ship)
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

# Player inventory
player_inventory = {"gold": 100, "goods": 0, "crew": 20}

# Update handle_menus to process port menu actions
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
                if result == "Buy Goods":
                    print("Buying goods...")
                    if player_inventory["gold"] >= port_menu.goods_cost:
                        player_inventory["goods"] += 1
                        player_inventory["gold"] -= port_menu.goods_cost
                    else:
                        print("Not enough gold!")
                elif result == "Sell Goods":
                    print("Selling goods...")
                    if player_inventory["goods"] > 0:
                        player_inventory["goods"] -= 1
                        player_inventory["gold"] += port_menu.goods_cost
                    else:
                        print("No goods to sell!")
                elif result == "Leave Port" or event.key == pygame.K_ESCAPE:
                    port_menu.close()
                    active_menu = None
    return None  # Continue normal gameplay

def handle_ship_collision(ship, islands):
    ship_center = pygame.Vector2(ship.x, ship.y)
    for island in islands:
        if ship.collides_with_island(ship.x, ship.y, islands, ship.width, ship.height):
            island_center = pygame.Vector2(island.x + island.width // 2, island.y + island.height // 2)
            direction = (ship_center - island_center)
            if direction.length() == 0:
                direction = pygame.Vector2(1, 0)  # Arbitrary direction if exactly overlapping
            direction = direction.normalize()
            ship.x += direction.x * 10  # Push the ship away from the island
            ship.y += direction.y * 10

class Plunder:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.collected = False

    def draw(self, screen, camera_offset_x, camera_offset_y):
        if not self.collected:
            pygame.draw.circle(screen, (255, 215, 0), (int(self.x - camera_offset_x), int(self.y - camera_offset_y)), 10)

    def check_collision(self, ship):
        ship_center = pygame.Vector2(ship.x, ship.y)
        plunder_center = pygame.Vector2(self.x, self.y)
        return ship_center.distance_to(plunder_center) < 20

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
    notification_duration = 20.0  # seconds

    # Player ship stats
    player_plunder = 0
    player_crew = 20

    # Create instances of Ship and Ocean
    ocean = Ocean(SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT)
    ship = Ship(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 20, 40)

    # Initialize plunders list
    plunders = []

    # Menus
    port_menu = PortMenu()
    tab_menu = TabMenu(ship)

    # Main game loop
    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        # Update procedural chunks based on player position
        update_chunks(ship.x, ship.y, ship)

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

        # Remove sunk NPC ships
        npc_ships = [npc for npc in npc_ships if not npc.sunk]
        for npc in npc_ships:
            npc.update(islands, dt=dt, player_ship=ship)
            npc.draw(screen, camera_offset_x, camera_offset_y)
            npc.update_cannonballs()
            npc.draw_cannonballs(screen, camera_offset_x, camera_offset_y)
            if not npc.sunk:
                npc.update(islands)
                for ball in ship.cannonballs:
                    if ball.alive and ball.collides_with_ship(npc):
                        npc.sunk = True
                        ball.alive = False
                        msg = f"Sank {npc.captain_name}'s ship {npc.ship_name}!"
                        notifications.append([msg, notification_duration])
                        plunders.append(Plunder(npc.x, npc.y, random.randint(10, 50)))  # Drop plunder
                npc.draw(screen, camera_offset_x, camera_offset_y)
            for ball in npc.cannonballs:
                if ball.alive and ball.collides_with_ship(ship):
                    ball.alive = False

        # Draw and collect plunder
        for plunder in plunders:
            plunder.draw(screen, camera_offset_x, camera_offset_y)
            if plunder.check_collision(ship):
                plunder.collected = True
                player_inventory["gold"] += plunder.value
                notifications.append([f"Collected {plunder.value} gold!", notification_duration])

        plunders = [p for p in plunders if not p.collected]

        # Player movement and logic
        next_x = ship.x
        next_y = ship.y
        rad = math.radians(ship.angle)
        next_x += -ship.speed * math.sin(rad)
        next_y += -ship.speed * math.cos(rad)

        if not ship.collides_with_island(next_x, next_y, islands, ship.width, ship.height):
            ship.x = next_x
            ship.y = next_y
        else:
            handle_ship_collision(ship, islands)
            ship.speed = 0  # Stop the ship if it would collide

        if active_menu is None:
            ship.update(pygame.key.get_pressed(), dt)

        # Update cannonballs
        ship.update_cannonballs()

        # Draw cannonballs
        ship.draw_cannonballs(screen, camera_offset_x, camera_offset_y)

        # Update notifications
        for note in notifications:
            note[1] -= dt
        notifications[:] = [n for n in notifications if n[1] > 0]

        # Draw overlay with player stats
        overlay_rect = pygame.Rect(10, 10, 200, 100)
        pygame.draw.rect(screen, (0, 0, 0), overlay_rect)  # Black background
        pygame.draw.rect(screen, (255, 255, 255), overlay_rect, 2)

        # Display player inventory and health
        inventory_lines = [
            f"Plunder: {player_plunder}",
            f"Crew: {player_inventory['crew']}",
            f"Gold: {player_inventory['gold']}",
            f"Goods: {player_inventory['goods']}"
        ]
        for i, line in enumerate(inventory_lines):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (overlay_rect.x + 10, overlay_rect.y + 10 + i * 22))

        # Draw notifications below the overlay
        notification_y = overlay_rect.y + overlay_rect.height + 10  # Position below the overlay
        for i, note in enumerate(notifications):
            text = font.render(note[0], True, (255, 200, 200))
            screen.blit(text, (10, notification_y + i * 22))

        # Interact prompt
        at_port = is_near_port(ship, islands)
        if at_port and not port_menu.active:
            prompt_text = font.render("Press F to interact with port", True, (255, 255, 255))
            screen.blit(prompt_text, (10, SCREEN_HEIGHT - 40))

        if active_menu == "tab":
            tab_menu.draw(screen, font)
        elif active_menu == "port":
            port_menu.draw(screen, font)

        # Update the display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()