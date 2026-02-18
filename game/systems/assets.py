from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pygame

from game.constants import SUIT_SHORT

if TYPE_CHECKING:
    from game.models.card import Card


SUIT_COLORS = {
    "spades": (28, 31, 43),
    "clubs": (28, 31, 43),
    "hearts": (204, 57, 77),
    "diamonds": (204, 57, 77),
}

TYPE_LABELS = {
    "monster": "MONSTRO",
    "potion": "POCAO",
    "weapon": "ESPADA",
}


class GameAssets:
    def __init__(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        assets_root = project_root / "assets"
        self.cards_dir = assets_root / "cards"
        self.icons_dir = assets_root / "icons"

        self._card_cache: dict[tuple[str, int, tuple[int, int]], pygame.Surface] = {}
        self._icon_cache: dict[tuple[str, tuple[int, int]], pygame.Surface] = {}
        self._fallback_font = pygame.font.SysFont("arial", 34, bold=True)
        self._fallback_small_font = pygame.font.SysFont("arial", 24, bold=True)

    def get_card_face(self, card: "Card", size: tuple[int, int]) -> pygame.Surface:
        key = (card.suit, card.rank, size)
        if key in self._card_cache:
            return self._card_cache[key]

        image_path = self.cards_dir / f"{card.suit}_{card.rank}.png"
        image = self._load_image(image_path, size)
        if image is None:
            image = self._build_fallback_card(card, size)

        self._card_cache[key] = image
        return image

    def get_type_icon(self, card_type: str, size: tuple[int, int]) -> pygame.Surface:
        key = (card_type, size)
        if key in self._icon_cache:
            return self._icon_cache[key]

        image_path = self.icons_dir / f"{card_type}.png"
        image = self._load_image(image_path, size)
        if image is None:
            image = self._build_fallback_icon(card_type, size)

        self._icon_cache[key] = image
        return image

    def _load_image(self, path: Path, size: tuple[int, int]) -> pygame.Surface | None:
        if not path.exists():
            return None
        image = pygame.image.load(path.as_posix()).convert_alpha()
        if image.get_size() != size:
            image = pygame.transform.smoothscale(image, size)
        return image

    def _build_fallback_card(self, card: "Card", size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        rect = surface.get_rect()
        pygame.draw.rect(surface, (245, 247, 252), rect, border_radius=18)
        pygame.draw.rect(surface, (21, 27, 39), rect, width=3, border_radius=18)

        color = SUIT_COLORS.get(card.suit, (33, 37, 49))
        corner = f"{card.rank_name}{SUIT_SHORT[card.suit]}"
        corner_label = self._fallback_font.render(corner, True, color)
        surface.blit(corner_label, (14, 10))

        bottom_label = self._fallback_font.render(corner, True, color)
        bottom_pos = bottom_label.get_rect(bottomright=(rect.width - 14, rect.height - 10))
        surface.blit(bottom_label, bottom_pos)

        suit_label = self._fallback_font.render(SUIT_SHORT[card.suit], True, color)
        suit_rect = suit_label.get_rect(center=(rect.centerx, rect.centery - 8))
        surface.blit(suit_label, suit_rect)

        type_label = self._fallback_small_font.render(TYPE_LABELS[card.card_type], True, (21, 27, 39))
        type_rect = type_label.get_rect(center=(rect.centerx, rect.centery + 44))
        surface.blit(type_label, type_rect)

        value_label = self._fallback_small_font.render(str(card.value), True, (21, 27, 39))
        value_rect = value_label.get_rect(center=(rect.centerx, rect.centery + 76))
        surface.blit(value_label, value_rect)
        return surface

    def _build_fallback_icon(self, card_type: str, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        rect = surface.get_rect()
        pygame.draw.circle(surface, (30, 37, 52), rect.center, min(rect.width, rect.height) // 2)

        label = TYPE_LABELS.get(card_type, "CARD")
        icon_text = self._fallback_small_font.render(label[:1], True, (240, 244, 255))
        icon_rect = icon_text.get_rect(center=rect.center)
        surface.blit(icon_text, icon_rect)
        return surface
