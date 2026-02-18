from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

import pygame

from game.constants import (
    ACCENT_COLOR,
    BG_COLOR,
    PANEL_COLOR,
    PLAYER_MAX_HP,
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
    def __init__(self, app: "GameApp", seed: str) -> None:
        super().__init__(app)
        self.seed = seed
        self.player = Player(max_hp=PLAYER_MAX_HP, hp=PLAYER_MAX_HP)
        self.deck = Deck(seed=seed, mode="original")

        self.card_sprites: list[CardSprite] = []
        self.resolve_timer = 0.0
        self.resolving_sprite: CardSprite | None = None
        self.run_over = False

        self.room_index = 1
        self.cards_taken_this_room = 0
        self.cards_required_this_room = 0
        self.room_started = False
        self.potion_used_this_room = False
        self.avoided_last_room = False

        self.last_card_type: str | None = None
        self.last_card_value = 0
        self.final_score = 0

        self.logs: deque[str] = deque(maxlen=7)
        self.logs.appendleft("Regras oficiais: sala de 4 cartas, escolhe 3 e deixa 1.")

        self.top_panel = pygame.Rect(0, 0, 1, 1)
        self.log_panel = pygame.Rect(0, 0, 1, 1)
        self.avoid_button_rect = pygame.Rect(0, 0, 1, 1)
        self.copy_seed_rect = pygame.Rect(0, 0, 1, 1)
        self.card_row_y = 0.0
        self.card_size = (170, 250)

        self._fill_room_to_four()
        self._begin_room_actions()
        self._layout_ui()

    def _add_log(self, message: str) -> None:
        self.logs.appendleft(message)

    def _fill_room_to_four(self) -> None:
        while len(self.card_sprites) < 4:
            drawn = self.deck.draw()
            if drawn is None:
                break
            self.card_sprites.append(CardSprite(card=drawn, center_x=0.0, center_y=0.0))

    def _begin_room_actions(self) -> None:
        self.cards_taken_this_room = 0
        self.potion_used_this_room = False
        self.room_started = False
        room_count = len(self.card_sprites)
        if room_count <= 0:
            self.cards_required_this_room = 0
        elif room_count == 1:
            self.cards_required_this_room = 1
        else:
            self.cards_required_this_room = min(3, room_count - 1)

    def _layout_ui(self) -> None:
        width, height = self.app.screen.get_size()
        self.top_panel = pygame.Rect(24, 16, width - 48, 178)
        self.log_panel = pygame.Rect(24, height - 196, width - 48, 172)
        self.copy_seed_rect = pygame.Rect(0, 0, 220, 40)
        self.copy_seed_rect.topright = (self.top_panel.right - 18, self.top_panel.top + 14)
        self.avoid_button_rect = pygame.Rect(0, 0, 220, 44)
        self.avoid_button_rect.bottomright = (self.top_panel.right - 18, self.top_panel.bottom - 16)

        available_h = self.log_panel.top - self.top_panel.bottom - 26
        available_h = max(190, available_h)
        card_h = min(300, max(190, int(available_h * 0.95)))
        card_w = int(card_h * 0.68)
        self.card_size = (card_w, card_h)
        self.card_row_y = self.top_panel.bottom + available_h / 2 + 3

        count = len(self.card_sprites)
        if count <= 0:
            return
        gap = max(20, int(card_w * 0.12))
        total_w = count * card_w + (count - 1) * gap
        start_x = width / 2 - total_w / 2 + card_w / 2
        for index, sprite in enumerate(self.card_sprites):
            sprite.center_x = start_x + index * (card_w + gap)
            sprite.center_y = self.card_row_y
            sprite.width = card_w
            sprite.height = card_h

    def _can_avoid_room(self) -> bool:
        return (
            len(self.card_sprites) == 4
            and not self.room_started
            and not self.avoided_last_room
            and self.resolve_timer <= 0
        )

    def _copy_seed(self) -> None:
        if self.app.copy_current_seed():
            self._add_log(f"Seed copiada para clipboard: {self.app.current_seed}")
        else:
            self._add_log("Nao foi possivel copiar a seed neste sistema.")

    def _avoid_room(self) -> None:
        if not self._can_avoid_room():
            self._add_log("Nao podes evitar esta sala agora.")
            return

        cards = [sprite.card for sprite in self.card_sprites]
        self.deck.place_many_bottom(cards)
        self.card_sprites.clear()
        self.room_index += 1
        self.avoided_last_room = True

        self._fill_room_to_four()
        self._begin_room_actions()
        self._layout_ui()
        self._add_log(f"Sala evitada. Entraste na sala {self.room_index}.")

    def _can_player_use_weapon_on(self, monster_value: int) -> bool:
        return self.player.can_use_weapon(monster_value)

    def _resolve_selected_card(self, card: "Card", prefer_weapon: bool) -> None:
        self.room_started = True
        self.avoided_last_room = False
        self.cards_taken_this_room += 1
        self.last_card_type = card.card_type
        self.last_card_value = card.value

        if card.card_type == "weapon":
            old_weapon = self.player.equip_weapon(card.value)
            if old_weapon == 0:
                self._add_log(f"Equipaste {card.short_name}. Poder da arma = {card.value}.")
            else:
                self._add_log(f"Trocaste arma {old_weapon} -> {card.value}.")
            return

        if card.card_type == "potion":
            if self.potion_used_this_room:
                self._add_log(f"Pocao {card.short_name} descartada (ja usaste uma nesta sala).")
                return
            healed = self.player.heal(card.value)
            self.potion_used_this_room = True
            self._add_log(f"Pocao {card.short_name}: curaste {healed} HP.")
            return

        used_weapon = prefer_weapon and self._can_player_use_weapon_on(card.value)
        if used_weapon:
            damage = self.player.fight_monster_with_weapon(card.value)
            self._add_log(
                f"Monstro {card.short_name} com arma {self.player.weapon_power}: dano recebido {damage}."
            )
            return

        if prefer_weapon and self.player.weapon_power > 0 and not self._can_player_use_weapon_on(card.value):
            self._add_log(
                f"Arma bloqueada contra {card.short_name} (valor deve ser <= {self.player.weapon_last_slain})."
            )

        damage = self.player.fight_monster_barehand(card.value)
        self._add_log(f"Monstro {card.short_name} na mao nua: levaste {damage} dano.")

    def _remaining_monster_value(self) -> int:
        room_monsters = sum(sprite.card.value for sprite in self.card_sprites if sprite.card.card_type == "monster")
        return room_monsters + self.deck.remaining_monster_value()

    def _finish_room_if_needed(self) -> None:
        if self.run_over:
            return

        if self.player.hp <= 0:
            self.final_score = self.player.hp - self._remaining_monster_value()
            self.run_over = True
            self.app.change_scene(
                "end",
                victory=False,
                rooms=max(1, self.room_index),
                monsters=self.player.monsters_defeated,
                hp=self.player.hp,
                score=self.final_score,
                seed=self.seed,
            )
            return

        if self.cards_taken_this_room < self.cards_required_this_room:
            return

        if self.deck.remaining == 0 and not self.card_sprites:
            bonus = 0
            if self.player.hp == self.player.max_hp and self.last_card_type == "potion":
                bonus = self.last_card_value
            self.final_score = self.player.hp + bonus
            self.run_over = True
            self.app.change_scene(
                "end",
                victory=True,
                rooms=max(1, self.room_index),
                monsters=self.player.monsters_defeated,
                hp=self.player.hp,
                score=self.final_score,
                seed=self.seed,
                perfect_potion_bonus=bonus,
            )
            return

        self.room_index += 1
        self._fill_room_to_four()
        self._begin_room_actions()
        self._layout_ui()
        self._add_log(f"Sala {self.room_index} iniciada.")

    def handle_event(self, event: pygame.event.Event) -> None:
        self._layout_ui()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.change_scene("menu")
                return
            if event.key == pygame.K_r:
                self.app.start_new_run(self.seed)
                return
            if event.key == pygame.K_a:
                self._avoid_room()
                return
            if event.key == pygame.K_c:
                self._copy_seed()
                return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button not in (1, 3):
            return
        if self.resolve_timer > 0 or self.player.hp <= 0:
            return

        if event.button == 1 and self.copy_seed_rect.collidepoint(event.pos):
            self._copy_seed()
            return
        if event.button == 1 and self.avoid_button_rect.collidepoint(event.pos):
            self._avoid_room()
            return

        for sprite in reversed(self.card_sprites):
            if sprite.contains(event.pos):
                prefer_weapon = event.button == 1
                if sprite.card.card_type != "monster":
                    prefer_weapon = False
                sprite.is_resolving = True
                sprite.trigger_click()
                self.resolving_sprite = sprite
                self.resolve_timer = 0.18
                self._resolve_selected_card(sprite.card, prefer_weapon=prefer_weapon)
                break

    def update(self, dt: float) -> None:
        self._layout_ui()
        mouse_pos = pygame.mouse.get_pos()
        can_interact = self.resolve_timer <= 0 and self.player.hp > 0

        for sprite in self.card_sprites:
            sprite_can_interact = can_interact and (not sprite.is_resolving)
            sprite.update(dt, mouse_pos, can_interact=sprite_can_interact)

        if self.resolve_timer > 0:
            self.resolve_timer = max(0.0, self.resolve_timer - dt)
            if self.resolve_timer == 0 and self.resolving_sprite is not None:
                if self.resolving_sprite in self.card_sprites:
                    self.card_sprites.remove(self.resolving_sprite)
                self.resolving_sprite = None
                self._layout_ui()
                self._finish_room_if_needed()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        self._draw_hud(surface)
        self._draw_cards(surface)
        self._draw_logs(surface)

    def _draw_hud(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, PANEL_COLOR, self.top_panel, border_radius=16)
        pygame.draw.rect(surface, (14, 16, 24), self.top_panel, width=3, border_radius=16)

        title = self.app.body_font.render("SCOUNDREL - MODO ORIGINAL", True, SUBTEXT_COLOR)
        surface.blit(title, (self.top_panel.x + 20, self.top_panel.y + 14))

        hp_label = self.app.body_font.render(
            f"HP: {self.player.hp}/{self.player.max_hp}", True, TEXT_COLOR
        )
        surface.blit(hp_label, (self.top_panel.x + 20, self.top_panel.y + 52))

        hp_bar_bg = pygame.Rect(self.top_panel.x + 154, self.top_panel.y + 58, 260, 22)
        pygame.draw.rect(surface, (50, 52, 64), hp_bar_bg, border_radius=8)
        ratio = self.player.hp / max(1, self.player.max_hp)
        hp_bar = hp_bar_bg.copy()
        hp_bar.width = max(0, int(hp_bar_bg.width * ratio))
        hp_color = (78, 196, 118) if ratio > 0.45 else (210, 120, 74)
        pygame.draw.rect(surface, hp_color, hp_bar, border_radius=8)

        weapon_text = f"Arma: {self.player.weapon_power}"
        if self.player.weapon_last_slain is not None:
            weapon_text += f" | limite <= {self.player.weapon_last_slain}"
        weapon_label = self.app.small_font.render(weapon_text, True, TEXT_COLOR)
        weapon_rect = weapon_label.get_rect(midleft=(self.top_panel.x + 440, self.top_panel.y + 68))
        surface.blit(weapon_label, weapon_rect)

        room_label = self.app.small_font.render(
            f"Sala {self.room_index} | Escolhas {self.cards_taken_this_room}/{self.cards_required_this_room}",
            True,
            TEXT_COLOR,
        )
        room_rect = room_label.get_rect(midleft=(self.top_panel.x + 20, self.top_panel.y + 106))
        surface.blit(room_label, room_rect)

        deck_label = self.app.small_font.render(
            f"Cartas no dungeon: {self.deck.remaining} | Seed: {self.seed}",
            True,
            TEXT_COLOR,
        )
        deck_rect = deck_label.get_rect(midleft=(self.top_panel.x + 20, self.top_panel.y + 136))
        surface.blit(deck_label, deck_rect)

        pygame.draw.rect(surface, (50, 77, 120), self.copy_seed_rect, border_radius=10)
        pygame.draw.rect(surface, (16, 24, 36), self.copy_seed_rect, width=2, border_radius=10)
        copy_text = self.app.small_font.render("COPIAR SEED (C)", True, (223, 232, 251))
        copy_rect = copy_text.get_rect(center=self.copy_seed_rect.center)
        surface.blit(copy_text, copy_rect)

        can_avoid = self._can_avoid_room()
        avoid_color = (80, 143, 211) if can_avoid else (67, 76, 96)
        pygame.draw.rect(surface, avoid_color, self.avoid_button_rect, border_radius=10)
        pygame.draw.rect(surface, (16, 24, 36), self.avoid_button_rect, width=2, border_radius=10)
        avoid_text = self.app.small_font.render("EVITAR SALA (A)", True, (228, 235, 251))
        avoid_rect = avoid_text.get_rect(center=self.avoid_button_rect.center)
        surface.blit(avoid_text, avoid_rect)

        tip = self.app.small_font.render(
            "Click esq. monstro: usa arma | Click dir.: mao nua | R reinicia seed | F11 fullscreen",
            True,
            SUBTEXT_COLOR,
        )
        tip_rect = tip.get_rect(midbottom=(self.top_panel.centerx, self.top_panel.bottom - 6))
        surface.blit(tip, tip_rect)

    def _draw_cards(self, surface: pygame.Surface) -> None:
        enabled = self.resolve_timer <= 0 and self.player.hp > 0
        draw_order = [sprite for sprite in self.card_sprites if not sprite.is_resolving]
        if self.resolving_sprite is not None:
            draw_order.append(self.resolving_sprite)

        for sprite in draw_order:
            sprite.draw(
                surface,
                title_font=self.app.card_title_font,
                detail_font=self.app.card_small_font,
                enabled=enabled and (not sprite.is_resolving),
                assets=self.app.assets,
            )

    def _draw_logs(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, PANEL_COLOR, self.log_panel, border_radius=16)
        pygame.draw.rect(surface, (14, 16, 24), self.log_panel, width=3, border_radius=16)

        header = self.app.body_font.render("LOG", True, ACCENT_COLOR)
        surface.blit(header, (self.log_panel.x + 18, self.log_panel.y + 10))

        y = self.log_panel.y + 48
        if not self.logs:
            empty = self.app.small_font.render("Sem eventos.", True, SUBTEXT_COLOR)
            surface.blit(empty, (self.log_panel.x + 18, y))
            return

        for line in self.logs:
            label = self.app.small_font.render(line, True, TEXT_COLOR)
            surface.blit(label, (self.log_panel.x + 18, y))
            y += 21
