from __future__ import annotations

import random
from typing import Iterable

from game.constants import SUITS
from game.models.card import Card


class Deck:
    def __init__(self, seed: int | str | None = None, mode: str = "original") -> None:
        self._rng = random.Random(seed)
        self._cards = [Card(suit, rank) for suit in SUITS for rank in range(1, 14) if self._include_card(mode, suit, rank)]
        self._rng.shuffle(self._cards)

    @staticmethod
    def _include_card(mode: str, suit: str, rank: int) -> bool:
        if mode != "original":
            return True
        if suit in ("hearts", "diamonds") and rank in (1, 11, 12, 13):
            return False
        return True

    def draw(self) -> Card | None:
        if not self._cards:
            return None
        return self._cards.pop()

    def place_many_bottom(self, cards: Iterable[Card]) -> None:
        group = list(cards)
        if not group:
            return
        self._cards[0:0] = group

    def remaining_monster_value(self) -> int:
        return sum(card.value for card in self._cards if card.card_type == "monster")

    @property
    def remaining(self) -> int:
        return len(self._cards)
