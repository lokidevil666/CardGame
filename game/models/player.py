from __future__ import annotations

from dataclasses import dataclass

from game.constants import PLAYER_MAX_HP


@dataclass(slots=True)
class Player:
    max_hp: int = PLAYER_MAX_HP
    hp: int = PLAYER_MAX_HP
    weapon_power: int = 0
    weapon_last_slain: int | None = None
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
        self.weapon_last_slain = None
        return old_value

    def can_use_weapon(self, monster_value: int) -> bool:
        if self.weapon_power <= 0:
            return False
        if self.weapon_last_slain is None:
            return True
        return monster_value <= self.weapon_last_slain

    def fight_monster_barehand(self, monster_value: int) -> int:
        self.take_damage(monster_value)
        self.monsters_defeated += 1
        return monster_value

    def fight_monster_with_weapon(self, monster_value: int) -> int:
        damage = max(0, monster_value - self.weapon_power)
        self.take_damage(damage)
        self.weapon_last_slain = monster_value
        self.monsters_defeated += 1
        return damage
