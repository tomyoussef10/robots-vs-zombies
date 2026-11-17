# Robots vs. Zombies

A turn-based role-playing game in Python, played in the terminal. You pick a difficulty, then fight robots, zombies, and other enemies one turn at a time, choosing which item to use and which enemy to hit.

Started as a class project at Stevens Institute of Technology and extended as a personal project.

## How to play

Requires Python 3.8 or newer. No extra packages needed.

```
python game.py
```

1. Pick a difficulty: Easy, Normal, or Hard.
2. Each turn, choose an item from your inventory and an enemy to target.
3. After your move, one living enemy strikes back.
4. Defeat an enemy to take its items. Defeat them all to win.

## Characters

| Character | Strategy | Special ability |
| --- | --- | --- |
| Character | Attacks the weakest opponent | None |
| Robot | Locks onto the first target | Double damage with electrical items |
| Zombie | Locks onto the first target | Double damage with viral items; carries 3 brain grenades |
| Healer | Attacks the weakest opponent | Heals itself with every hit |
| Boss | Attacks the weakest opponent | A tougher zombie with a single-use "plague roar" |
| You | Your choice | Start with 2 health potions |

## How the code is organized

- `Character` holds everything every fighter shares: health, inventory, looting, and the attack logic in `perform_move`.
- Subclasses change behavior by overriding two small methods: `choose_target` (who to attack) and the `bonus_damage_type` setting (which items deal double damage). The battle loop never needs to know which kind of character it is dealing with.
- `ask_for_number` keeps asking until the player enters a valid choice, so a typo can't crash the game.

## Tests

```
python -m unittest
```

Tests cover damage bonuses, consumable items, health limits, looting, and input validation.

## What I added beyond the original assignment

- Input validation so invalid entries no longer crash the game
- Two new character classes: Healer and Boss
- Three difficulty levels
- Health potions and a maximum-health cap
- Shared damage-bonus system that replaced duplicated code in each subclass
- Unit tests
