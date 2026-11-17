"""Unit tests for game.py. Run with: python -m unittest"""
import unittest
from unittest.mock import patch
from game import Item, Move, Character, Robot, Zombie, Healer, Boss, ask_for_number


class TestBattleRules(unittest.TestCase):
    def test_robot_doubles_electrical_damage(self):
        robot, target = Robot("R", 10), Character("T", 10)
        baton = Item("shock baton", 1, 0, "electrical", False)
        robot.perform_move(Move(target, baton))
        self.assertEqual(target.health_points, 8)

    def test_zombie_grenade_is_consumed(self):
        zombie, target = Zombie("Z", 10), Character("T", 50)
        grenade = Item("brain grenade", 5, 0, "viral", True)
        zombie.perform_move(Move(target, grenade))
        self.assertEqual(target.health_points, 40)
        self.assertEqual(zombie.inventory[grenade], 2)

    def test_health_never_goes_below_zero(self):
        boss, target = Boss("B", 14), Character("T", 3)
        boss.perform_move(boss.get_next_move([target]))
        self.assertEqual(target.health_points, 0)

    def test_healer_cannot_exceed_max_health(self):
        healer, target = Healer("H", 6), Character("T", 10)
        healer.perform_move(healer.get_next_move([target]))
        self.assertEqual(healer.health_points, 6)

    def test_loot_transfer_empties_source(self):
        winner, loser = Character("W", 5), Zombie("L", 5)
        winner.transfer_loot(loser.inventory)
        self.assertTrue(all(qty == 0 for qty in loser.inventory.values()))
        grenade = Item("brain grenade", 5, 0, "viral", True)
        self.assertEqual(winner.inventory[grenade], 3)


class TestInputValidation(unittest.TestCase):
    @patch("builtins.print")
    @patch("builtins.input", side_effect=["abc", "0", "9", "2"])
    def test_rejects_bad_input_until_valid(self, _input, _print):
        self.assertEqual(ask_for_number("> ", 3), 2)


if __name__ == "__main__":
    unittest.main()
