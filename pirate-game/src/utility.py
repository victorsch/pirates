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

if __name__ == "__main__":
    print("Random Pirate Ship Name:", generate_ship_name())
    print("Random Pirate Captain Name:", generate_captain_name())