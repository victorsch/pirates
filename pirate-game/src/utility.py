import random

SHIP_PREFIXES = [
    "Black", "Bloody", "Golden", "Crimson", "Sable", "Sea", "Stormy", "Wicked", "Salty", "Iron", "Scarlet", "Ghostly"
]
SHIP_SUFFIXES = [
    "Pearl", "Fortune", "Dagger", "Revenge", "Serpent", "Wraith", "Cutlass", "Galleon", "Corsair", "Tempest", "Mariner", "Maiden"
]
SHIP_TITLES = [
    "The", "Queen's", "King's", "Lady", "Captain's", "Admiral's"
]

CAPTAIN_FIRST = [
    "Jack", "Anne", "Edward", "Mary", "Charles", "Henry", "Grace", "Samuel", "Bartholomew", "Charlotte", "Benjamin", "Morgan"
]
CAPTAIN_NICKNAMES = [
    "Blackbeard", "Redhand", "Silver", "the Cruel", "the Bold", "the Mad", "the Sly", "the Ruthless", "the Swift", "the Dread"
]
CAPTAIN_LAST = [
    "Rackham", "Bonny", "Teach", "Read", "Vane", "Low", "Drake", "Roberts", "Morgan", "Kidd", "Flint", "Sparrow"
]

ISLAND_PREFIXES = ["Mystic", "Hidden", "Lost", "Forbidden", "Ancient", "Emerald", "Golden", "Stormy", "Silent", "Shadow", "Crystal", "Scarlet"]
ISLAND_SUFFIXES = ["Cove", "Lagoon", "Isle", "Bay", "Haven", "Reef", "Shores", "Sanctuary", "Harbor", "Atoll", "Peninsula", "Paradise"]
ISLAND_TITLES = ["The", "Elder", "Sacred", "Pirate's", "Captain's", "Admiral's"]

PORT_PREFIXES = ["Port", "Harbor", "Dock", "Bay", "Wharf", "Marina", "Quay", "Pier", "Landing", "Haven", "Anchorage", "Terminal"]
PORT_SUFFIXES = ["Royal", "Trade", "Storm", "Shadow", "Golden", "Emerald", "Scarlet", "Iron", "Sea", "Wind", "Wave", "Tide"]
PORT_TITLES = ["The", "King's", "Queen's", "Admiral's", "Captain's", "Pirate's"]

def generate_ship_name():
    if random.random() < 0.3:
        # Sometimes use a title
        return f"{random.choice(SHIP_TITLES)} {random.choice(SHIP_PREFIXES)} {random.choice(SHIP_SUFFIXES)}"
    else:
        return f"{random.choice(SHIP_PREFIXES)} {random.choice(SHIP_SUFFIXES)}"

def generate_captain_name():
    if random.random() < 0.5:
        # Sometimes use a nickname
        return f"{random.choice(CAPTAIN_FIRST)} '{random.choice(CAPTAIN_NICKNAMES)}' {random.choice(CAPTAIN_LAST)}"
    else:
        return f"{random.choice(CAPTAIN_FIRST)} {random.choice(CAPTAIN_LAST)}"

def generate_island_name():
    if random.random() < 0.3:
        # Sometimes use a title
        return f"{random.choice(ISLAND_TITLES)} {random.choice(ISLAND_PREFIXES)} {random.choice(ISLAND_SUFFIXES)}"
    else:
        return f"{random.choice(ISLAND_PREFIXES)} {random.choice(ISLAND_SUFFIXES)}"

def generate_port_name():
    if random.random() < 0.3:
        # Sometimes use a title
        return f"{random.choice(PORT_TITLES)} {random.choice(PORT_PREFIXES)} {random.choice(PORT_SUFFIXES)}"
    else:
        return f"{random.choice(PORT_PREFIXES)} {random.choice(PORT_SUFFIXES)}"

if __name__ == "__main__":
    print("Random Pirate Ship Name:", generate_ship_name())
    print("Random Pirate Captain Name:", generate_captain_name())
    print("Random Island Name:", generate_island_name())
    print("Random Port Name:", generate_port_name())