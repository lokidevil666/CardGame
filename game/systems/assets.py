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

BASE_CARD_SIZE = (176, 260)
BASE_ICON_SIZE = (320, 320)

SUIT_PATTERNS = {
    "hearts": [
        "01100110",
        "11111111",
        "11111111",
        "11111111",
        "01111110",
        "00111100",
        "00011000",
    ],
    "diamonds": [
        "00011000",
        "00111100",
        "01111110",
        "11111111",
        "01111110",
        "00111100",
        "00011000",
    ],
    "clubs": [
        "00011000",
        "01111110",
        "11111111",
        "01111110",
        "11111111",
        "00111100",
        "00111100",
    ],
    "spades": [
        "00011000",
        "00111100",
        "01111110",
        "11111111",
        "11111111",
        "00111100",
        "00111100",
    ],
}


class GameAssets:
    def __init__(self) -> None:
        project_root = Path(__file__).resolve().parents[2]
        assets_root = project_root / "assets"
        self.icons_dir = assets_root / "icons"

        self._card_sources: dict[tuple[str, int], pygame.Surface] = {}
        self._icon_sources: dict[str, pygame.Surface] = {}
        self._rank_font = pygame.font.SysFont("couriernew", 30, bold=True)
        self._small_font = pygame.font.SysFont("couriernew", 13, bold=True)
        self._fallback_small_font = pygame.font.SysFont("couriernew", 20, bold=True)

    def get_card_face(self, card: "Card", size: tuple[int, int]) -> pygame.Surface:
        source_key = (card.suit, card.rank)
        if source_key not in self._card_sources:
            self._card_sources[source_key] = self._build_pixel_card(card, BASE_CARD_SIZE)

        source = self._card_sources[source_key]
        if source.get_size() == size:
            return source
        return pygame.transform.scale(source, size)

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

    @staticmethod
    def _draw_pattern(
        surface: pygame.Surface,
        pattern: list[str],
        pixel_size: int,
        offset_x: int,
        offset_y: int,
        color: tuple[int, int, int],
    ) -> None:
        for y, row in enumerate(pattern):
            for x, bit in enumerate(row):
                if bit == "1":
                    rect = pygame.Rect(
                        offset_x + x * pixel_size,
                        offset_y + y * pixel_size,
                        pixel_size,
                        pixel_size,
                    )
                    pygame.draw.rect(surface, color, rect)

    def _build_pixel_card(self, card: "Card", size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        rect = surface.get_rect()
        pygame.draw.rect(surface, (16, 19, 26), rect)

        outer = pygame.Rect(2, 2, rect.width - 4, rect.height - 4)
        inner = pygame.Rect(6, 6, rect.width - 12, rect.height - 12)
        pygame.draw.rect(surface, (231, 236, 249), outer)
        pygame.draw.rect(surface, (244, 247, 255), inner)
        pygame.draw.rect(surface, (43, 49, 67), outer, width=2)

        color = SUIT_COLORS.get(card.suit, (33, 37, 49))
        corner = f"{card.rank_name}{SUIT_SHORT[card.suit]}"
        corner_label = self._rank_font.render(corner, False, color)
        surface.blit(corner_label, (12, 8))

        bottom_label = self._rank_font.render(corner, False, color)
        bottom_pos = bottom_label.get_rect(bottomright=(rect.width - 12, rect.height - 8))
        surface.blit(bottom_label, bottom_pos)

        pattern = SUIT_PATTERNS[card.suit]
        self._draw_pattern(surface, pattern, pixel_size=3, offset_x=18, offset_y=48, color=color)
        self._draw_pattern(
            surface,
            pattern,
            pixel_size=3,
            offset_x=rect.width - 18 - len(pattern[0]) * 3,
            offset_y=rect.height - 48 - len(pattern) * 3,
            color=color,
        )
        self._draw_pattern(
            surface,
            pattern,
            pixel_size=7,
            offset_x=rect.centerx - (len(pattern[0]) * 7) // 2,
            offset_y=rect.centery - (len(pattern) * 7) // 2 - 10,
            color=color,
        )

        type_label = self._small_font.render(TYPE_LABELS[card.card_type], False, (34, 39, 56))
        type_rect = type_label.get_rect(midbottom=(rect.centerx, rect.bottom - 10))
        surface.blit(type_label, type_rect)
        return surface

    def _build_fallback_icon(self, card_type: str, size: tuple[int, int]) -> pygame.Surface:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        rect = surface.get_rect()
        pygame.draw.rect(surface, (30, 37, 52), rect)
        pygame.draw.rect(surface, (72, 85, 111), rect, width=10)

        label = TYPE_LABELS.get(card_type, "CARD")
        icon_text = self._fallback_small_font.render(label[:1], False, (240, 244, 255))
        icon_rect = icon_text.get_rect(center=rect.center)
        surface.blit(icon_text, icon_rect)
        return surface
