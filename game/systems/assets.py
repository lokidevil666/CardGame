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

BASE_CARD_SIZE = (420, 620)
BASE_ICON_SIZE = (320, 320)


class GameAssets:
    def __init__(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        assets_root = project_root / "assets"
        self.cards_dir = assets_root / "cards"
        self.icons_dir = assets_root / "icons"

        self._card_sources: dict[tuple[str, int], pygame.Surface] = {}
        self._icon_sources: dict[str, pygame.Surface] = {}
        self._fallback_font = pygame.font.SysFont("arial", 34, bold=True)
        self._fallback_small_font = pygame.font.SysFont("arial", 24, bold=True)

    def get_card_face(self, card: "Card", size: tuple[int, int]) -> pygame.Surface:
        source_key = (card.suit, card.rank)
        if source_key not in self._card_sources:
            image_path = self.cards_dir / f"{card.suit}_{card.rank}.png"
            image = self._load_image(image_path)
            if image is None:
                image = self._build_fallback_card(card, BASE_CARD_SIZE)
            self._card_sources[source_key] = image

        source = self._card_sources[source_key]
        if source.get_size() == size:
            return source
        return pygame.transform.smoothscale(source, size)

    def get_type_icon(self, card_type: str, size: tuple[int, int]) -> pygame.Surface:
        if card_type not in self._icon_sources:
            image_path = self.icons_dir / f"{card_type}.png"
            image = self._load_image(image_path)
            if image is None:
                image = self._build_fallback_icon(card_type, BASE_ICON_SIZE)
            self._icon_sources[card_type] = image

        source = self._icon_sources[card_type]
        if source.get_size() == size:
            return source
        return pygame.transform.smoothscale(source, size)

    def _load_image(self, path: Path) -> pygame.Surface | None:
        if not path.exists():
            return None
        return pygame.image.load(path.as_posix()).convert_alpha()

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
