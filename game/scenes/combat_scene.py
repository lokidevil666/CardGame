from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

import pygame

from game.constants import (
    ACCENT_COLOR,
    BG_COLOR,
    CARD_GAP,
    CARD_WIDTH,
    PANEL_COLOR,
    ROOM_VISIBLE_CARDS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SUBTEXT_COLOR,
    TEXT_COLOR,
)
from game.models.deck import Deck
from game.models.player import Player
from game.scenes.base_scene import BaseScene
from game.systems.card_sprite import CardSprite

if TYPE_CHECKING:
    from game.game_app import GameApp
    from game.models.card import Card


class CombatScene(BaseScene):
    def __init__(self, app: "GameApp") -> None:
        super().__init__(app)
        self.player = Player()
        self.deck = Deck()

        self.card_sprites: list[CardSprite] = []
        self.slot_centers = self._build_slots()
        self.card_row_y = 330

        self.resolve_timer = 0.0
        self.resolving_sprite: CardSprite | None = None
        self.run_over = False
        self.turn_index = 0

        self.logs: deque[str] = deque(maxlen=6)
        self._add_log("Run iniciada. Clica numa carta para agir.")

        self._fill_room()

    def _build_slots(self) -> list[float]:
        total_w = ROOM_VISIBLE_CARDS * CARD_WIDTH + (ROOM_VISIBLE_CARDS - 1) * CARD_GAP
        start_x = SCREEN_WIDTH / 2 - total_w / 2 + CARD_WIDTH / 2
        return [start_x + i * (CARD_WIDTH + CARD_GAP) for i in range(ROOM_VISIBLE_CARDS)]

    def _add_log(self, message: str) -> None:
        self.logs.appendleft(message)

    def _fill_room(self) -> None:
        while len(self.card_sprites) < ROOM_VISIBLE_CARDS:
            drawn = self.deck.draw()
            if drawn is None:
                break
            x = self.slot_centers[len(self.card_sprites)]
            self.card_sprites.append(CardSprite(card=drawn, center_x=x, center_y=self.card_row_y))

    def _reflow_cards(self) -> None:
        for index, sprite in enumerate(self.card_sprites):
            sprite.center_x = self.slot_centers[index]

    def _resolve_card(self, card: "Card") -> None:
        self.turn_index += 1
        card_type = card.card_type
        if card_type == "monster":
            raw_damage = card.value
            if self.player.weapon_power > 0:
                damage = max(1, raw_damage - self.player.weapon_power)
            else:
                damage = raw_damage
            self.player.take_damage(damage)
            self.player.monsters_defeated += 1
            self._add_log(
                f"Turno {self.turn_index}: Monstro {card.short_name} atacou "
                f"({raw_damage}) -> levaste {damage} dano."
            )
            return

        if card_type == "potion":
            healed = self.player.heal(card.value)
            self._add_log(
                f"Turno {self.turn_index}: Pocao {card.short_name} curou {healed} HP "
                f"(valor base {card.value})."
            )
            return

        old_weapon = self.player.equip_weapon(card.value)
        if old_weapon == 0:
            self._add_log(
                f"Turno {self.turn_index}: Espada {card.short_name} equipada "
                f"com poder {card.value}."
            )
        else:
            self._add_log(
                f"Turno {self.turn_index}: Troca de espada {old_weapon} -> {card.value}."
            )

    def _check_end_conditions(self) -> None:
        if self.run_over:
            return

        if self.player.hp <= 0:
            self.run_over = True
            self.app.change_scene(
                "end",
                victory=False,
                turns=self.turn_index,
                monsters=self.player.monsters_defeated,
            )
            return

        if self.deck.remaining == 0 and not self.card_sprites:
            self.run_over = True
            self.app.change_scene(
                "end",
                victory=True,
                turns=self.turn_index,
                monsters=self.player.monsters_defeated,
                hp=self.player.hp,
            )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.change_scene("menu")
                return
            if event.key == pygame.K_r:
                self.app.change_scene("combat")
                return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        if self.resolve_timer > 0 or self.player.hp <= 0:
            return

        for sprite in reversed(self.card_sprites):
            if sprite.contains(event.pos):
                sprite.is_resolving = True
                sprite.trigger_click()
                self.resolving_sprite = sprite
                self.resolve_timer = 0.22
                self._resolve_card(sprite.card)
                break

    def update(self, dt: float) -> None:
        mouse_pos = pygame.mouse.get_pos()
        can_interact = self.resolve_timer <= 0 and self.player.hp > 0

        for sprite in self.card_sprites:
            sprite_can_interact = can_interact and (not sprite.is_resolving)
            sprite.update(dt, mouse_pos, can_interact=sprite_can_interact)

        if self.resolve_timer > 0:
            self.resolve_timer = max(0.0, self.resolve_timer - dt)
            if self.resolve_timer == 0 and self.resolving_sprite is not None:
                self.card_sprites.remove(self.resolving_sprite)
                self.resolving_sprite = None
                self._reflow_cards()
                self._fill_room()
                self._check_end_conditions()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        self._draw_hud(surface)
        self._draw_cards(surface)
        self._draw_logs(surface)

    def _draw_hud(self, surface: pygame.Surface) -> None:
        top_panel = pygame.Rect(24, 18, SCREEN_WIDTH - 48, 145)
        pygame.draw.rect(surface, PANEL_COLOR, top_panel, border_radius=16)
        pygame.draw.rect(surface, (14, 16, 24), top_panel, width=3, border_radius=16)

        title = self.app.body_font.render("SALA ATUAL", True, SUBTEXT_COLOR)
        surface.blit(title, (top_panel.x + 22, top_panel.y + 16))

        hp_label = self.app.body_font.render(
            f"HP: {self.player.hp}/{self.player.max_hp}", True, TEXT_COLOR
        )
        surface.blit(hp_label, (top_panel.x + 22, top_panel.y + 52))

        hp_bar_bg = pygame.Rect(top_panel.x + 150, top_panel.y + 57, 280, 24)
        pygame.draw.rect(surface, (50, 52, 64), hp_bar_bg, border_radius=8)
        ratio = self.player.hp / self.player.max_hp
        hp_bar = hp_bar_bg.copy()
        hp_bar.width = max(0, int(hp_bar_bg.width * ratio))
        hp_color = (78, 196, 118) if ratio > 0.45 else (210, 120, 74)
        pygame.draw.rect(surface, hp_color, hp_bar, border_radius=8)

        weapon_label = self.app.body_font.render(
            f"Espada equipada: {self.player.weapon_power}", True, TEXT_COLOR
        )
        weapon_rect = weapon_label.get_rect(midleft=(top_panel.x + 470, top_panel.y + 65))
        surface.blit(weapon_label, weapon_rect)

        deck_label = self.app.body_font.render(
            f"Cartas no baralho: {self.deck.remaining}", True, TEXT_COLOR
        )
        deck_rect = deck_label.get_rect(midleft=(top_panel.x + 760, top_panel.y + 65))
        surface.blit(deck_label, deck_rect)

        tip = self.app.small_font.render(
            "ESC: menu | R: reiniciar run | Clicar carta: resolver acao",
            True,
            SUBTEXT_COLOR,
        )
        tip_rect = tip.get_rect(midtop=(top_panel.centerx, top_panel.bottom - 34))
        surface.blit(tip, tip_rect)

    def _draw_cards(self, surface: pygame.Surface) -> None:
        enabled = self.resolve_timer <= 0 and self.player.hp > 0
        draw_order = [s for s in self.card_sprites if not s.is_resolving]
        if self.resolving_sprite is not None:
            draw_order.append(self.resolving_sprite)

        for sprite in draw_order:
            sprite.draw(
                surface,
                title_font=self.app.title_font,
                body_font=self.app.body_font,
                small_font=self.app.small_font,
                enabled=enabled and (not sprite.is_resolving),
            )

    def _draw_logs(self, surface: pygame.Surface) -> None:
        log_panel = pygame.Rect(24, SCREEN_HEIGHT - 190, SCREEN_WIDTH - 48, 162)
        pygame.draw.rect(surface, PANEL_COLOR, log_panel, border_radius=16)
        pygame.draw.rect(surface, (14, 16, 24), log_panel, width=3, border_radius=16)

        header = self.app.body_font.render("LOG DE COMBATE", True, ACCENT_COLOR)
        surface.blit(header, (log_panel.x + 18, log_panel.y + 12))

        y = log_panel.y + 46
        if not self.logs:
            empty = self.app.small_font.render("Sem eventos ainda.", True, SUBTEXT_COLOR)
            surface.blit(empty, (log_panel.x + 18, y))
            return

        for line in self.logs:
            label = self.app.small_font.render(line, True, TEXT_COLOR)
            surface.blit(label, (log_panel.x + 18, y))
            y += 22
