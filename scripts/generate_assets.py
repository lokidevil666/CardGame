from __future__ import annotations

import os
from pathlib import Path

import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


CARD_SIZE = (420, 620)
ICON_SIZE = (320, 320)

RANK_TEXT = {
    1: "A",
    11: "J",
    12: "Q",
    13: "K",
}

SUITS = ("spades", "clubs", "hearts", "diamonds")
SUIT_COLORS = {
    "spades": (28, 31, 43),
    "clubs": (28, 31, 43),
    "hearts": (204, 57, 77),
    "diamonds": (204, 57, 77),
}


def _draw_heart(surface: pygame.Surface, color: tuple[int, int, int]) -> None:
    w, h = surface.get_size()
    radius = int(min(w, h) * 0.24)
    pygame.draw.circle(surface, color, (int(w * 0.34), int(h * 0.33)), radius)
    pygame.draw.circle(surface, color, (int(w * 0.66), int(h * 0.33)), radius)
    points = [(w * 0.12, h * 0.38), (w * 0.88, h * 0.38), (w * 0.50, h * 0.90)]
    pygame.draw.polygon(surface, color, points)


def _draw_diamond(surface: pygame.Surface, color: tuple[int, int, int]) -> None:
    w, h = surface.get_size()
    points = [(w * 0.50, h * 0.08), (w * 0.90, h * 0.50), (w * 0.50, h * 0.92), (w * 0.10, h * 0.50)]
    pygame.draw.polygon(surface, color, points)


def _draw_club(surface: pygame.Surface, color: tuple[int, int, int]) -> None:
    w, h = surface.get_size()
    radius = int(min(w, h) * 0.22)
    pygame.draw.circle(surface, color, (int(w * 0.50), int(h * 0.26)), radius)
    pygame.draw.circle(surface, color, (int(w * 0.30), int(h * 0.53)), radius)
    pygame.draw.circle(surface, color, (int(w * 0.70), int(h * 0.53)), radius)
    stem_rect = pygame.Rect(0, 0, int(w * 0.22), int(h * 0.34))
    stem_rect.center = (int(w * 0.50), int(h * 0.80))
    pygame.draw.rect(surface, color, stem_rect, border_radius=max(4, int(w * 0.06)))


def _draw_spade(surface: pygame.Surface, color: tuple[int, int, int]) -> None:
    w, h = surface.get_size()
    radius = int(min(w, h) * 0.22)
    pygame.draw.circle(surface, color, (int(w * 0.34), int(h * 0.42)), radius)
    pygame.draw.circle(surface, color, (int(w * 0.66), int(h * 0.42)), radius)
    points = [(w * 0.12, h * 0.48), (w * 0.88, h * 0.48), (w * 0.50, h * 0.08)]
    pygame.draw.polygon(surface, color, points)
    stem_rect = pygame.Rect(0, 0, int(w * 0.22), int(h * 0.34))
    stem_rect.center = (int(w * 0.50), int(h * 0.80))
    pygame.draw.rect(surface, color, stem_rect, border_radius=max(4, int(w * 0.06)))


def draw_suit_symbol(suit: str, size: int) -> pygame.Surface:
    symbol = pygame.Surface((size, size), pygame.SRCALPHA)
    color = SUIT_COLORS[suit]
    if suit == "hearts":
        _draw_heart(symbol, color)
    elif suit == "diamonds":
        _draw_diamond(symbol, color)
    elif suit == "clubs":
        _draw_club(symbol, color)
    else:
        _draw_spade(symbol, color)
    return symbol


def create_card_image(
    suit: str,
    rank: int,
    rank_font: pygame.font.Font,
    small_font: pygame.font.Font,
) -> pygame.Surface:
    surface = pygame.Surface(CARD_SIZE, pygame.SRCALPHA)
    rect = surface.get_rect()

    bg = pygame.Rect(18, 18, rect.width - 36, rect.height - 36)
    pygame.draw.rect(surface, (246, 248, 254), bg, border_radius=28)
    pygame.draw.rect(surface, (24, 28, 39), bg, width=4, border_radius=28)

    rank_label = RANK_TEXT.get(rank, str(rank))
    color = SUIT_COLORS[suit]
    text = rank_font.render(rank_label, True, color)
    surface.blit(text, (bg.left + 22, bg.top + 18))
    mirrored = rank_font.render(rank_label, True, color)
    mirror_rect = mirrored.get_rect(bottomright=(bg.right - 22, bg.bottom - 18))
    surface.blit(mirrored, mirror_rect)

    corner_symbol = draw_suit_symbol(suit, 56)
    corner_rect = corner_symbol.get_rect(topleft=(bg.left + 30, bg.top + 108))
    surface.blit(corner_symbol, corner_rect)

    corner_bottom = draw_suit_symbol(suit, 56)
    corner_bottom_rect = corner_bottom.get_rect(bottomright=(bg.right - 30, bg.bottom - 108))
    surface.blit(corner_bottom, corner_bottom_rect)

    center_symbol = draw_suit_symbol(suit, 210)
    center_symbol.set_alpha(130)
    center_rect = center_symbol.get_rect(center=bg.center)
    surface.blit(center_symbol, center_rect)

    label = small_font.render("BARALHO NORMAL", True, (74, 82, 103))
    label_rect = label.get_rect(midbottom=(bg.centerx, bg.bottom - 20))
    surface.blit(label, label_rect)
    return surface


def create_monster_icon() -> pygame.Surface:
    surface = pygame.Surface(ICON_SIZE, pygame.SRCALPHA)
    rect = surface.get_rect()
    pygame.draw.circle(surface, (71, 85, 130), rect.center, 126)
    pygame.draw.polygon(surface, (196, 83, 85), [(92, 84), (130, 28), (160, 96)])
    pygame.draw.polygon(surface, (196, 83, 85), [(228, 96), (258, 28), (292, 84)])
    pygame.draw.circle(surface, (250, 250, 250), (130, 150), 32)
    pygame.draw.circle(surface, (250, 250, 250), (192, 150), 32)
    pygame.draw.circle(surface, (19, 24, 34), (130, 150), 14)
    pygame.draw.circle(surface, (19, 24, 34), (192, 150), 14)
    mouth = pygame.Rect(0, 0, 148, 72)
    mouth.center = (160, 220)
    pygame.draw.ellipse(surface, (23, 28, 42), mouth)
    for i in range(5):
        x = 116 + i * 24
        tooth = [(x, 208), (x + 12, 236), (x + 24, 208)]
        pygame.draw.polygon(surface, (244, 244, 244), tooth)
    return surface


def create_potion_icon() -> pygame.Surface:
    surface = pygame.Surface(ICON_SIZE, pygame.SRCALPHA)
    neck = pygame.Rect(0, 0, 46, 74)
    neck.center = (160, 82)
    pygame.draw.rect(surface, (66, 75, 94), neck, border_radius=10)

    cork = pygame.Rect(0, 0, 54, 18)
    cork.center = (160, 40)
    pygame.draw.rect(surface, (173, 128, 77), cork, border_radius=6)

    body_points = [(86, 90), (234, 90), (266, 250), (54, 250)]
    pygame.draw.polygon(surface, (89, 112, 146), body_points)
    pygame.draw.polygon(surface, (39, 48, 66), body_points, width=7)

    liquid = pygame.Rect(74, 156, 172, 84)
    pygame.draw.ellipse(surface, (89, 193, 139), liquid)
    highlight = pygame.Rect(102, 112, 30, 96)
    pygame.draw.ellipse(surface, (220, 238, 255, 120), highlight)
    bubble_a = pygame.Rect(0, 0, 18, 18)
    bubble_a.center = (128, 178)
    bubble_b = pygame.Rect(0, 0, 12, 12)
    bubble_b.center = (182, 194)
    pygame.draw.ellipse(surface, (223, 255, 238), bubble_a)
    pygame.draw.ellipse(surface, (223, 255, 238), bubble_b)
    return surface


def create_weapon_icon() -> pygame.Surface:
    surface = pygame.Surface(ICON_SIZE, pygame.SRCALPHA)

    blade = [(160, 38), (198, 144), (182, 252), (138, 252), (122, 144)]
    pygame.draw.polygon(surface, (218, 228, 241), blade)
    pygame.draw.polygon(surface, (84, 97, 122), blade, width=6)
    pygame.draw.line(surface, (142, 155, 182), (160, 52), (160, 252), width=5)

    crossguard = pygame.Rect(0, 0, 164, 24)
    crossguard.center = (160, 256)
    pygame.draw.rect(surface, (190, 149, 76), crossguard, border_radius=10)
    pygame.draw.rect(surface, (90, 67, 36), crossguard, width=4, border_radius=10)

    grip = pygame.Rect(0, 0, 32, 84)
    grip.center = (160, 312)
    pygame.draw.rect(surface, (87, 63, 42), grip, border_radius=8)
    pygame.draw.rect(surface, (48, 34, 23), grip, width=3, border_radius=8)

    pommel = pygame.Rect(0, 0, 54, 40)
    pommel.center = (160, 356)
    pygame.draw.ellipse(surface, (174, 130, 65), pommel)
    pygame.draw.ellipse(surface, (90, 67, 36), pommel, width=4)
    return surface


def generate_assets(project_root: Path) -> None:
    cards_dir = project_root / "assets" / "cards"
    icons_dir = project_root / "assets" / "icons"
    cards_dir.mkdir(parents=True, exist_ok=True)
    icons_dir.mkdir(parents=True, exist_ok=True)

    pygame.init()
    pygame.font.init()

    rank_font = pygame.font.SysFont("arial", 86, bold=True)
    small_font = pygame.font.SysFont("arial", 34, bold=True)

    for suit in SUITS:
        for rank in range(1, 14):
            image = create_card_image(suit, rank, rank_font, small_font)
            output = cards_dir / f"{suit}_{rank}.png"
            pygame.image.save(image, output.as_posix())

    icons = {
        "monster": create_monster_icon(),
        "potion": create_potion_icon(),
        "weapon": create_weapon_icon(),
    }
    for name, icon in icons.items():
        output = icons_dir / f"{name}.png"
        pygame.image.save(icon, output.as_posix())

    pygame.quit()


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    generate_assets(root)
    print("Assets gerados em assets/cards e assets/icons.")
