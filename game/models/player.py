from __future__ import annotations

from dataclasses import dataclass

from game.constants import PLAYER_MAX_HP


@dataclass(slots=True)
class Player:
    max_hp: int = PLAYER_MAX_HP
    hp: int = PLAYER_MAX_HP
    weapon_power: int = 0
    monsters_defeated: int = 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    def heal(self, amount: int) -> int:
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def equip_weapon(self, value: int) -> int:
        old_value = self.weapon_power
        self.weapon_power = value
        return old_value
