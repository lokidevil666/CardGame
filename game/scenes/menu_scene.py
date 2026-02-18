from __future__ import annotations

import math

import pygame

from game.constants import ACCENT_COLOR, BG_COLOR, PANEL_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH, SUBTEXT_COLOR, TEXT_COLOR
from game.scenes.base_scene import BaseScene


class MenuScene(BaseScene):
    def __init__(self, app: "GameApp") -> None:
        super().__init__(app)
        self._pulse_time = 0.0
        self.start_rect = pygame.Rect(0, 0, 300, 68)
        self.start_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.app.change_scene("combat")
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_rect.collidepoint(event.pos):
                self.app.change_scene("combat")

    def update(self, dt: float) -> None:
        self._pulse_time += dt

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)

        panel = pygame.Rect(0, 0, 980, 490)
        panel.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.rect(surface, PANEL_COLOR, panel, border_radius=20)
        pygame.draw.rect(surface, (16, 18, 26), panel, width=3, border_radius=20)

        title = self.app.title_font.render("SCOUNDREL ROGUELIKE", True, TEXT_COLOR)
        title_rect = title.get_rect(midtop=(SCREEN_WIDTH // 2, panel.top + 32))
        surface.blit(title, title_rect)

        subtitle = self.app.body_font.render(
            "Cartas de um baralho normal, com combate e sobrevivencia.", True, SUBTEXT_COLOR
        )
        subtitle_rect = subtitle.get_rect(midtop=(SCREEN_WIDTH // 2, title_rect.bottom + 12))
        surface.blit(subtitle, subtitle_rect)

        rules = [
            "ESPADAS + PAUS = CRIATURAS (causam dano)",
            "COPAS = POCOES DE VIDA (curam HP)",
            "OUROS = ESPADAS (equipam defesa para os combates)",
            "Sobrevive ate limpar o baralho inteiro.",
        ]
        y = subtitle_rect.bottom + 44
        for line in rules:
            label = self.app.body_font.render(line, True, TEXT_COLOR)
            rect = label.get_rect(midtop=(SCREEN_WIDTH // 2, y))
            surface.blit(label, rect)
            y += 42

        pulse = 0.5 + 0.5 * (1 + math.sin(self._pulse_time * 3.5))
        glow = int(ACCENT_COLOR[0] + (255 - ACCENT_COLOR[0]) * (pulse * 0.2))
        button_color = (glow, ACCENT_COLOR[1], ACCENT_COLOR[2])
        pygame.draw.rect(surface, button_color, self.start_rect, border_radius=16)
        pygame.draw.rect(surface, (20, 26, 42), self.start_rect, width=3, border_radius=16)

        button_text = self.app.body_font.render("INICIAR RUN (ENTER)", True, (18, 24, 36))
        button_text_rect = button_text.get_rect(center=self.start_rect.center)
        surface.blit(button_text, button_text_rect)
