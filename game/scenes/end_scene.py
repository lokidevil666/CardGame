from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from game.constants import ACCENT_COLOR, BG_COLOR, PANEL_COLOR, SUBTEXT_COLOR, TEXT_COLOR
from game.scenes.base_scene import BaseScene

if TYPE_CHECKING:
    from game.game_app import GameApp


class EndScene(BaseScene):
    def __init__(
        self,
        app: "GameApp",
        *,
        victory: bool,
        rooms: int = 0,
        monsters: int = 0,
        hp: int = 0,
        score: int = 0,
        seed: str = "",
        perfect_potion_bonus: int = 0,
    ) -> None:
        super().__init__(app)
        self.victory = victory
        self.rooms = rooms
        self.monsters = monsters
        self.hp = hp
        self.score = score
        self.seed = seed
        self.perfect_potion_bonus = perfect_potion_bonus

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_r:
            self.app.start_new_run(self.seed)
        elif event.key == pygame.K_m:
            self.app.change_scene("menu")
        elif event.key == pygame.K_c:
            self.app.copy_text(self.seed)
        elif event.key == pygame.K_ESCAPE:
            self.app.running = False

    def update(self, dt: float) -> None:
        _ = dt

    def render(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        surface.fill(BG_COLOR)

        panel = pygame.Rect(0, 0, min(860, width - 80), min(500, height - 80))
        panel.center = (width // 2, height // 2)
        pygame.draw.rect(surface, PANEL_COLOR, panel, border_radius=20)
        pygame.draw.rect(surface, (15, 18, 25), panel, width=3, border_radius=20)

        title_text = "VITORIA!" if self.victory else "DERROTA!"
        title_color = (102, 214, 130) if self.victory else (225, 118, 98)
        title = self.app.title_font.render(title_text, True, title_color)
        title_rect = title.get_rect(midtop=(panel.centerx, panel.top + 34))
        surface.blit(title, title_rect)

        subtitle_text = (
            "Limpaste todo o baralho e sobreviveste."
            if self.victory
            else "A tua vida chegou a zero antes do fim da run."
        )
        subtitle = self.app.body_font.render(subtitle_text, True, SUBTEXT_COLOR)
        subtitle_rect = subtitle.get_rect(midtop=(panel.centerx, title_rect.bottom + 10))
        surface.blit(subtitle, subtitle_rect)

        stats = [
            f"Salas jogadas: {self.rooms}",
            f"Criaturas enfrentadas: {self.monsters}",
            f"HP final: {self.hp}",
            f"Score final: {self.score}",
            f"Seed: {self.seed}",
        ]
        if self.victory and self.perfect_potion_bonus > 0:
            stats.append(f"Bonus de pocao perfeita: +{self.perfect_potion_bonus}")

        y = subtitle_rect.bottom + 42
        for stat in stats:
            label = self.app.body_font.render(stat, True, TEXT_COLOR)
            label_rect = label.get_rect(midtop=(panel.centerx, y))
            surface.blit(label, label_rect)
            y += 42

        controls = self.app.small_font.render(
            "R: nova run (mesma seed) | C: copiar seed | M: menu | ESC: sair",
            True,
            ACCENT_COLOR,
        )
        controls_rect = controls.get_rect(midbottom=(panel.centerx, panel.bottom - 26))
        surface.blit(controls, controls_rect)
