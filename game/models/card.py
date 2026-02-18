from __future__ import annotations

from dataclasses import dataclass

from game.constants import RANK_NAMES, SUIT_SHORT


@dataclass(frozen=True, slots=True)
class Card:
    suit: str
    rank: int

    @property
    def card_type(self) -> str:
        if self.suit in ("spades", "clubs"):
            return "monster"
        if self.suit == "hearts":
            return "potion"
        return "weapon"

    @property
    def value(self) -> int:
        return self.rank

    @property
    def rank_name(self) -> str:
        return RANK_NAMES.get(self.rank, str(self.rank))

    @property
    def short_name(self) -> str:
        return f"{self.rank_name}{SUIT_SHORT[self.suit]}"
