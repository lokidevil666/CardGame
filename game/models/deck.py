from __future__ import annotations

import random
from typing import Optional

from game.constants import SUITS
from game.models.card import Card


class Deck:
    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)
        self._cards = [Card(suit, rank) for suit in SUITS for rank in range(1, 14)]
        self._rng.shuffle(self._cards)

    def draw(self) -> Card | None:
        if not self._cards:
            return None
        return self._cards.pop()

    @property
    def remaining(self) -> int:
        return len(self._cards)
