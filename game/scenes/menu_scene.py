from __future__ import annotations

import math

import pygame

from game.constants import ACCENT_COLOR, BG_COLOR, PANEL_COLOR, SUBTEXT_COLOR, TEXT_COLOR
from game.scenes.base_scene import BaseScene


class MenuScene(BaseScene):
    def __init__(self, app: "GameApp") -> None:
        super().__init__(app)
        self._pulse_time = 0.0
        self.seed_input = app.current_seed
        self.seed_active = False
        self.feedback_text = ""
        self.feedback_timer = 0.0

        self.start_rect = pygame.Rect(0, 0, 1, 1)
        self.seed_rect = pygame.Rect(0, 0, 1, 1)
        self.copy_rect = pygame.Rect(0, 0, 1, 1)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._start_game()
                return
            if event.key == pygame.K_SPACE and not self.seed_active:
                self._start_game()
                return
            if event.key == pygame.K_TAB:
                self.seed_active = not self.seed_active
                return
            if event.key == pygame.K_ESCAPE:
                self.app.running = False
                return
            if event.key == pygame.K_c and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                self._copy_seed()
                return

            if self.seed_active:
                if event.key == pygame.K_BACKSPACE:
                    self.seed_input = self.seed_input[:-1]
                elif event.key in (pygame.K_DELETE,):
                    self.seed_input = ""
                else:
                    if event.unicode and event.unicode.isprintable() and len(self.seed_input) < 32:
                        self.seed_input += event.unicode
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_rect.collidepoint(event.pos):
                self._start_game()
            elif self.copy_rect.collidepoint(event.pos):
                self._copy_seed()
            else:
                self.seed_active = self.seed_rect.collidepoint(event.pos)

    def _show_feedback(self, text: str) -> None:
        self.feedback_text = text
        self.feedback_timer = 2.5

    def _copy_seed(self) -> None:
        text = self.seed_input.strip() or self.app.current_seed
        if not text:
            self._show_feedback("Nenhuma seed para copiar.")
            return
        if self.app.copy_text(text):
            self._show_feedback(f"Seed copiada: {text}")
            return
        self._show_feedback("Clipboard indisponivel neste sistema.")

    def _start_game(self) -> None:
        self.app.start_new_run(self.seed_input)
        self._show_feedback(f"Run iniciada com seed {self.app.current_seed}")

    def update(self, dt: float) -> None:
        self._pulse_time += dt
        if self.feedback_timer > 0:
            self.feedback_timer = max(0.0, self.feedback_timer - dt)

    def _build_layout(self, width: int, height: int) -> pygame.Rect:
        panel_w = min(1020, width - 80)
        panel_h = min(620, height - 80)
        panel = pygame.Rect(0, 0, panel_w, panel_h)
        panel.center = (width // 2, height // 2)

        self.seed_rect = pygame.Rect(0, 0, min(560, panel_w - 120), 56)
        self.seed_rect.midtop = (panel.centerx, panel.top + 320)

        self.copy_rect = pygame.Rect(0, 0, 170, 44)
        self.copy_rect.topleft = (self.seed_rect.left, self.seed_rect.bottom + 10)

        self.start_rect = pygame.Rect(0, 0, min(360, panel_w - 180), 66)
        self.start_rect.midbottom = (panel.centerx, panel.bottom - 44)
        return panel

    def render(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        surface.fill(BG_COLOR)

        panel = self._build_layout(width, height)
        pygame.draw.rect(surface, PANEL_COLOR, panel, border_radius=20)
        pygame.draw.rect(surface, (16, 18, 26), panel, width=3, border_radius=20)

        title = self.app.title_font.render("SCOUNDREL ROGUELIKE", True, TEXT_COLOR)
        title_rect = title.get_rect(midtop=(panel.centerx, panel.top + 24))
        surface.blit(title, title_rect)

        subtitle = self.app.body_font.render(
            "Regras oficiais de Scoundrel com visual em pixel art.", True, SUBTEXT_COLOR
        )
        subtitle_rect = subtitle.get_rect(midtop=(panel.centerx, title_rect.bottom + 8))
        surface.blit(subtitle, subtitle_rect)

        rules = [
            "Vida inicial: 20 | Valor das cartas: A=14, J=11, Q=12, K=13.",
            "Sala tem 4 cartas: podes evitar (A), mas nao em duas salas seguidas.",
            "Ao jogar uma sala, resolves 3 cartas e deixas 1 para a sala seguinte.",
            "Copas: 1 pocao por sala. Ouros: arma nova substitui a antiga.",
            "Monstros (Paus/Espadas): click esquerdo usa arma, direito usa mao nua.",
        ]
        y = subtitle_rect.bottom + 24
        for line in rules:
            label = self.app.small_font.render(line, True, TEXT_COLOR)
            rect = label.get_rect(midtop=(panel.centerx, y))
            surface.blit(label, rect)
            y += 34

        seed_label = self.app.small_font.render("Seed (opcional):", True, SUBTEXT_COLOR)
        seed_label_rect = seed_label.get_rect(midleft=(self.seed_rect.left, self.seed_rect.top - 26))
        surface.blit(seed_label, seed_label_rect)

        seed_bg_color = (20, 28, 44) if self.seed_active else (25, 31, 47)
        pygame.draw.rect(surface, seed_bg_color, self.seed_rect, border_radius=10)
        border = (144, 202, 255) if self.seed_active else (66, 88, 128)
        pygame.draw.rect(surface, border, self.seed_rect, width=2, border_radius=10)

        seed_text = self.seed_input if self.seed_input else "deixa vazio para seed aleatoria"
        seed_color = TEXT_COLOR if self.seed_input else (129, 140, 166)
        seed_render = self.app.small_font.render(seed_text, True, seed_color)
        seed_render_rect = seed_render.get_rect(midleft=(self.seed_rect.left + 14, self.seed_rect.centery))
        surface.blit(seed_render, seed_render_rect)

        pygame.draw.rect(surface, (58, 81, 119), self.copy_rect, border_radius=10)
        pygame.draw.rect(surface, (19, 26, 41), self.copy_rect, width=2, border_radius=10)
        copy_label = self.app.small_font.render("COPIAR", True, (223, 231, 250))
        copy_rect = copy_label.get_rect(center=self.copy_rect.center)
        surface.blit(copy_label, copy_rect)

        pulse = 0.5 + 0.5 * (1 + math.sin(self._pulse_time * 3.5))
        glow = int(ACCENT_COLOR[0] + (255 - ACCENT_COLOR[0]) * (pulse * 0.2))
        button_color = (glow, ACCENT_COLOR[1], ACCENT_COLOR[2])
        pygame.draw.rect(surface, button_color, self.start_rect, border_radius=16)
        pygame.draw.rect(surface, (20, 26, 42), self.start_rect, width=3, border_radius=16)

        button_text = self.app.body_font.render("INICIAR RUN (ENTER)", True, (18, 24, 36))
        button_text_rect = button_text.get_rect(center=self.start_rect.center)
        surface.blit(button_text, button_text_rect)

        controls = self.app.small_font.render(
            "TAB ativa seed | CTRL+C copia seed | F11 fullscreen | ESC sair",
            True,
            SUBTEXT_COLOR,
        )
        controls_rect = controls.get_rect(midbottom=(panel.centerx, panel.bottom - 8))
        surface.blit(controls, controls_rect)

        if self.feedback_timer > 0 and self.feedback_text:
            feedback = self.app.small_font.render(self.feedback_text, True, ACCENT_COLOR)
            feedback_rect = feedback.get_rect(midbottom=(panel.centerx, self.start_rect.top - 16))
            surface.blit(feedback, feedback_rect)
