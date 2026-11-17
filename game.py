"""
Robots vs. Zombies: a turn-based RPG in Python.

Author: Thomas Youssef

Started as a CS 115 project at Stevens Institute of Technology and
extended as a personal project with input validation, new character
classes, difficulty levels, and a shared damage-bonus system.
"""

import random


class Item:
    """An item a character can use in battle."""

    def __init__(self, name, damage_points, regeneration_points, damage_type, is_consumable):
        self.name = name
        self.damage_points = damage_points
        self.regeneration_points = regeneration_points
        self.damage_type = damage_type
        self.is_consumable = is_consumable

    def __str__(self):
        parts = [f"{self.name} (damage {self.damage_points}"]
        if self.regeneration_points:
            parts.append(f", heals {self.regeneration_points}")
        parts.append(f", {self.damage_type}")
        if self.is_consumable:
            parts.append(", single use")
        return "".join(parts) + ")"

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        # Items compare by total value, so characters pick the most useful one
        return (self.damage_points + self.regeneration_points) < (
            other.damage_points + other.regeneration_points)

    def __hash__(self):
        return hash((self.name, self.damage_points, self.regeneration_points,
                     self.damage_type, self.is_consumable))

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        return (self.name, self.damage_points, self.regeneration_points,
                self.damage_type, self.is_consumable) == (
                other.name, other.damage_points, other.regeneration_points,
                other.damage_type, other.is_consumable)


class Move:
    """An action a character takes in a turn: which item, used on whom."""

    def __init__(self, other_character, item):
        self.other_character = other_character
        self.item = item


class Character:
    """Base class. Subclasses change behavior by overriding the hooks below."""

    # Item damage type that this character deals double damage with (None = no bonus)
    bonus_damage_type = None

    def __init__(self, name, max_health_points):
        self.name = name
        self.max_health_points = max_health_points
        self.health_points = max_health_points
        self.inventory = {Item("rusty axe", 1, 0, "physical", False): 1}

    def __str__(self):
        return f"{self.name} ({self.health_points}/{self.max_health_points} HP)"

    def __lt__(self, other):
        return self.health_points < other.health_points

    def is_alive(self):
        return self.health_points > 0

    def usable_items(self):
        return [item for item, qty in self.inventory.items() if qty > 0]

    def damage_multiplier(self, item):
        """Polymorphism hook: subclasses get bonus damage for their item type."""
        return 2 if item.damage_type == self.bonus_damage_type else 1

    def choose_target(self, other_characters):
        """Default strategy: attack the weakest opponent."""
        return min(other_characters)

    def get_next_move(self, other_characters):
        return Move(self.choose_target(other_characters), max(self.usable_items()))

    def transfer_loot(self, loot):
        """Move every item from loot into this character's inventory."""
        for item, qty in loot.items():
            if qty > 0:
                self.inventory[item] = self.inventory.get(item, 0) + qty
                loot[item] = 0

    def perform_move(self, move):
        """Apply a move and return a short description of what happened."""
        item, target = move.item, move.other_character
        if item is None or self.inventory.get(item, 0) == 0:
            return f"{self.name} fumbles and does nothing."

        damage = item.damage_points * self.damage_multiplier(item)
        target.health_points = max(0, target.health_points - damage)
        self.health_points = min(self.max_health_points,
                                 self.health_points + item.regeneration_points)
        if item.is_consumable:
            self.inventory[item] -= 1

        message = f"{self.name} uses {item.name} on {target.name} for {damage} damage"
        if item.regeneration_points:
            message += f" and heals {item.regeneration_points}"
        return message + "."


class Robot(Character):
    bonus_damage_type = "electrical"

    def __init__(self, name, max_health_points):
        super().__init__(name, max_health_points)
        self.inventory[Item("shock baton", 1, 0, "electrical", False)] = 1

    def choose_target(self, other_characters):
        # Robots always lock onto the first target they see
        return other_characters[0]


class Zombie(Character):
    bonus_damage_type = "viral"

    def __init__(self, name, max_health_points):
        super().__init__(name, max_health_points)
        self.inventory[Item("brain grenade", 5, 0, "viral", True)] = 3

    def choose_target(self, other_characters):
        return other_characters[0]


class Healer(Character):
    """New class: weak attacks, but heals itself every turn."""

    def __init__(self, name, max_health_points):
        super().__init__(name, max_health_points)
        self.inventory[Item("healing staff", 1, 2, "holy", False)] = 1


class Boss(Zombie):
    """New class: a tougher zombie with a powerful single-use attack."""

    def __init__(self, name, max_health_points):
        super().__init__(name, max_health_points)
        self.inventory[Item("plague roar", 6, 0, "viral", True)] = 1

    def choose_target(self, other_characters):
        return min(other_characters)


class PlayableCharacter(Character):
    """The player. Moves come from keyboard input, validated so bad input can't crash the game."""

    def __init__(self, name, max_health_points):
        super().__init__(name, max_health_points)
        self.inventory[Item("health potion", 0, 5, "healing", True)] = 2

    def get_next_move(self, other_characters):
        items = self.usable_items()
        print("\nYour items:")
        for i, item in enumerate(items, start=1):
            print(f"  {i}. {item}  x{self.inventory[item]}")
        item = items[ask_for_number("Choose an item number: ", len(items)) - 1]

        print("Enemies:")
        for i, enemy in enumerate(other_characters, start=1):
            print(f"  {i}. {enemy}")
        target = other_characters[ask_for_number("Choose an enemy number: ", len(other_characters)) - 1]
        return Move(target, item)


def ask_for_number(prompt, highest):
    """Keep asking until the player enters a whole number from 1 to highest."""
    while True:
        answer = input(prompt).strip()
        if answer.isdigit() and 1 <= int(answer) <= highest:
            return int(answer)
        print(f"Please enter a number from 1 to {highest}.")


# Each difficulty builds a fresh set of enemies, so every game starts clean
DIFFICULTIES = {
    "1": ("Easy", 20, lambda: [Character("Basic Cube", 4), Robot("Shock Drone", 5)]),
    "2": ("Normal", 15, lambda: [Zombie("Rotting Walker", 8), Robot("Shock Drone", 6),
                                 Character("Basic Cube", 4)]),
    "3": ("Hard", 15, lambda: [Zombie("Rotting Walker", 8), Robot("Shock Drone", 6),
                               Healer("Field Medic", 6), Boss("Zombie King", 14)]),
}


def choose_difficulty():
    print("Choose a difficulty:")
    for key, (label, _, make_enemies) in DIFFICULTIES.items():
        print(f"  {key}. {label} ({len(make_enemies())} enemies)")
    key = str(ask_for_number("Difficulty: ", len(DIFFICULTIES)))
    label, player_hp, make_enemies = DIFFICULTIES[key]
    enemies = make_enemies()
    print(f"\n{label} mode. Defeat all {len(enemies)} enemies to win!")
    return player_hp, enemies


def battle_round(player, enemies, attacker):
    """One round: the player moves, then one living enemy strikes back."""
    move = player.get_next_move(enemies)
    print(player.perform_move(move))
    target = move.other_character
    if not target.is_alive():
        print(f"{target.name} is defeated! You take its items.")
        player.transfer_loot(target.inventory)
        return

    print(attacker.perform_move(attacker.get_next_move([player])))
    if not player.is_alive():
        attacker.transfer_loot(player.inventory)


def main():
    print("=== Robots vs. Zombies ===")
    player_hp, enemies = choose_difficulty()
    player = PlayableCharacter("You", player_hp)

    while True:
        enemies = [e for e in enemies if e.is_alive()]
        if not enemies:
            print("\nYou win!")
            break
        print(f"\n{player}")
        battle_round(player, enemies, random.choice(enemies))
        if not player.is_alive():
            print("\nYou were defeated!")
            break


if __name__ == "__main__":
    main()
