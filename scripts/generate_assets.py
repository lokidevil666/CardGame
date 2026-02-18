from __future__ import annotations

import os
from pathlib import Path

import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


PIXEL_GRID = 32
PIXEL_SCALE = 10
ICON_SIZE = (PIXEL_GRID * PIXEL_SCALE, PIXEL_GRID * PIXEL_SCALE)


def _pixel_canvas() -> pygame.Surface:
    return pygame.Surface((PIXEL_GRID, PIXEL_GRID), pygame.SRCALPHA)


def _upscale(surface: pygame.Surface) -> pygame.Surface:
    return pygame.transform.scale(surface, ICON_SIZE)


def create_monster_icon() -> pygame.Surface:
    low = _pixel_canvas()
    low.fill((24, 32, 56, 0))

    pygame.draw.rect(low, (64, 83, 130), (5, 8, 22, 17))
    pygame.draw.rect(low, (45, 57, 90), (5, 8, 22, 3))
    pygame.draw.polygon(low, (196, 80, 90), [(7, 8), (10, 2), (13, 8)])
    pygame.draw.polygon(low, (196, 80, 90), [(19, 8), (22, 2), (25, 8)])

    pygame.draw.rect(low, (246, 248, 252), (10, 13, 4, 4))
    pygame.draw.rect(low, (246, 248, 252), (18, 13, 4, 4))
    pygame.draw.rect(low, (20, 24, 34), (11, 14, 2, 2))
    pygame.draw.rect(low, (20, 24, 34), (19, 14, 2, 2))

    pygame.draw.rect(low, (19, 24, 37), (9, 20, 14, 3))
    for x in (10, 13, 16, 19, 22):
        pygame.draw.rect(low, (244, 244, 244), (x, 20, 1, 2))
    return _upscale(low)


def create_potion_icon() -> pygame.Surface:
    low = _pixel_canvas()
    low.fill((0, 0, 0, 0))

    pygame.draw.rect(low, (158, 115, 67), (13, 2, 6, 2))
    pygame.draw.rect(low, (71, 84, 112), (13, 4, 6, 4))
    pygame.draw.rect(low, (51, 62, 90), (10, 8, 12, 16))
    pygame.draw.rect(low, (37, 45, 67), (10, 8, 12, 1))
    pygame.draw.rect(low, (37, 45, 67), (10, 8, 1, 16))
    pygame.draw.rect(low, (37, 45, 67), (21, 8, 1, 16))
    pygame.draw.rect(low, (37, 45, 67), (10, 23, 12, 1))

    pygame.draw.rect(low, (88, 194, 142), (11, 16, 10, 7))
    pygame.draw.rect(low, (214, 236, 255), (13, 10, 2, 7))
    pygame.draw.rect(low, (232, 255, 238), (18, 18, 1, 1))
    pygame.draw.rect(low, (232, 255, 238), (15, 20, 1, 1))
    return _upscale(low)


def create_weapon_icon() -> pygame.Surface:
    low = _pixel_canvas()
    low.fill((0, 0, 0, 0))

    pygame.draw.polygon(low, (214, 226, 240), [(16, 2), (19, 11), (17, 22), (15, 22), (13, 11)])
    pygame.draw.polygon(low, (95, 110, 140), [(16, 2), (19, 11), (17, 22), (15, 22), (13, 11)], width=1)
    pygame.draw.line(low, (150, 166, 196), (16, 4), (16, 22))

    pygame.draw.rect(low, (186, 145, 72), (10, 22, 12, 2))
    pygame.draw.rect(low, (88, 66, 38), (10, 22, 12, 1))
    pygame.draw.rect(low, (88, 66, 38), (15, 24, 2, 5))
    pygame.draw.rect(low, (171, 132, 70), (14, 29, 4, 2))
    return _upscale(low)


def generate_assets(project_root: Path) -> None:
    icons_dir = project_root / "assets" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)

    old_cards = project_root / "assets" / "cards"
    if old_cards.exists():
        for png in old_cards.glob("*.png"):
            png.unlink()

    pygame.init()
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
    print("Icons pixel art gerados em assets/icons. Faces de baralho removidas.")
