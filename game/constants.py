from __future__ import annotations


SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

CARD_WIDTH = 170
CARD_HEIGHT = 250
CARD_GAP = 35
ROOM_VISIBLE_CARDS = 4

PLAYER_MAX_HP = 30

BG_COLOR = (20, 22, 32)
PANEL_COLOR = (34, 38, 52)
TEXT_COLOR = (236, 238, 244)
SUBTEXT_COLOR = (186, 190, 208)
ACCENT_COLOR = (108, 170, 255)

CARD_COLORS = {
    "monster": (180, 70, 75),
    "potion": (74, 165, 109),
    "weapon": (90, 120, 185),
}

SUITS = ("spades", "clubs", "hearts", "diamonds")
SUIT_SHORT = {
    "spades": "S",
    "clubs": "C",
    "hearts": "H",
    "diamonds": "D",
}

RANK_NAMES = {
    1: "A",
    11: "J",
    12: "Q",
    13: "K",
}
