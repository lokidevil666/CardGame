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
from game.models.card import Card
from game.models.deck import Deck
from game.models.player import Player
from game.scenes.base_scene import BaseScene
from game.systems.card_sprite import CardSprite

if TYPE_CHECKING:
    from game.game_app import GameApp


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
        self.board_rect = pygame.Rect(0, 0, 1, 1)
        self.deck_slot_rect = pygame.Rect(0, 0, 1, 1)
        self.weapon_slot_rect = pygame.Rect(0, 0, 1, 1)
        self.room_slot_rects: list[pygame.Rect] = []
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
        self.top_panel = pygame.Rect(24, 16, width - 48, 96)
        self.log_panel = pygame.Rect(24, height - 132, width - 48, 108)
        self.copy_seed_rect = pygame.Rect(0, 0, 220, 40)
        self.copy_seed_rect.topright = (self.top_panel.right - 14, self.top_panel.top + 10)
        self.avoid_button_rect = pygame.Rect(0, 0, 220, 40)
        self.avoid_button_rect.topright = (self.top_panel.right - 14, self.top_panel.top + 52)

        self.board_rect = pygame.Rect(
            24,
            self.top_panel.bottom + 8,
            width - 48,
            self.log_panel.top - self.top_panel.bottom - 16,
        )

        available_h = self.board_rect.height
        card_h = min(180, max(130, int(available_h * 0.30)))
        card_w = int(card_h * 0.68)
        self.card_size = (card_w, card_h)

        deck_center = (self.board_rect.centerx, self.board_rect.top + card_h // 2 + 2)
        self.deck_slot_rect = pygame.Rect(0, 0, card_w, card_h)
        self.deck_slot_rect.center = deck_center

        weapon_center = (self.board_rect.centerx, self.board_rect.bottom - card_h // 2 - 2)
        self.weapon_slot_rect = pygame.Rect(0, 0, card_w, card_h)
        self.weapon_slot_rect.center = weapon_center

        row_y = self.board_rect.centery
        gap = max(18, int(card_w * 0.16))
        total_w = 4 * card_w + 3 * gap
        start_x = self.board_rect.centerx - total_w / 2 + card_w / 2
        self.room_slot_rects = []
        for index in range(4):
            slot = pygame.Rect(0, 0, card_w, card_h)
            slot.center = (int(start_x + index * (card_w + gap)), int(row_y))
            self.room_slot_rects.append(slot)

        for index, sprite in enumerate(self.card_sprites):
            slot_index = min(index, len(self.room_slot_rects) - 1)
            slot = self.room_slot_rects[slot_index]
            sprite.center_x = slot.centerx
            sprite.center_y = slot.centery
            sprite.width = card_w
            sprite.height = card_h

    def _can_avoid_room(self) -> bool:
        return (
            len(self.card_sprites) == 4
            and not self.room_started
            and not self.avoided_last_room
            and self.resolve_timer <= 0
        )

    @staticmethod
    def _rank_from_value(value: int) -> int:
        if value == 14:
            return 1
        return max(1, min(13, value))

    def _equipped_weapon_card(self) -> Card | None:
        if self.player.weapon_power <= 0:
            return None
        return Card("diamonds", self._rank_from_value(self.player.weapon_power))

    @staticmethod
    def _draw_slot_outline(
        surface: pygame.Surface,
        rect: pygame.Rect,
        color: tuple[int, int, int],
        border: int = 4,
    ) -> None:
        pygame.draw.rect(surface, color, rect.inflate(8, 8), width=border, border_radius=10)

    def _draw_card_back(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        pygame.draw.rect(surface, (37, 36, 68), rect, border_radius=12)
        pygame.draw.rect(surface, (17, 19, 30), rect, width=3, border_radius=12)
        inner = rect.inflate(-16, -16)
        pygame.draw.rect(surface, (58, 61, 112), inner, border_radius=8)
        pygame.draw.rect(surface, (23, 27, 49), inner, width=2, border_radius=8)

        cell = max(6, rect.width // 12)
        for y in range(inner.top + 6, inner.bottom - 2, cell):
            for x in range(inner.left + 6, inner.right - 2, cell):
                color = (90, 95, 164) if (x // cell + y // cell) % 2 == 0 else (72, 77, 140)
                pixel = pygame.Rect(x, y, max(3, cell - 2), max(3, cell - 2))
                pygame.draw.rect(surface, color, pixel)

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

        title = self.app.small_font.render("SCOUNDREL | Layout: Deck / Sala / Arma", True, SUBTEXT_COLOR)
        surface.blit(title, (self.top_panel.x + 16, self.top_panel.y + 8))

        hp_label = self.app.small_font.render(
            f"HP {self.player.hp}/{self.player.max_hp}", True, TEXT_COLOR
        )
        surface.blit(hp_label, (self.top_panel.x + 16, self.top_panel.y + 36))

        hp_bar_bg = pygame.Rect(self.top_panel.x + 145, self.top_panel.y + 42, 210, 18)
        pygame.draw.rect(surface, (50, 52, 64), hp_bar_bg, border_radius=8)
        ratio = self.player.hp / max(1, self.player.max_hp)
        hp_bar = hp_bar_bg.copy()
        hp_bar.width = max(0, int(hp_bar_bg.width * ratio))
        hp_color = (78, 196, 118) if ratio > 0.45 else (210, 120, 74)
        pygame.draw.rect(surface, hp_color, hp_bar, border_radius=8)

        weapon_text = f"Arma {self.player.weapon_power}"
        if self.player.weapon_last_slain is not None:
            weapon_text += f" | limite <= {self.player.weapon_last_slain}"
        weapon_label = self.app.small_font.render(weapon_text, True, TEXT_COLOR)
        weapon_rect = weapon_label.get_rect(midleft=(self.top_panel.x + 370, self.top_panel.y + 52))
        surface.blit(weapon_label, weapon_rect)

        room_label = self.app.small_font.render(
            f"Sala {self.room_index}  Escolhas {self.cards_taken_this_room}/{self.cards_required_this_room}  Dungeon {self.deck.remaining}",
            True,
            TEXT_COLOR,
        )
        room_rect = room_label.get_rect(midleft=(self.top_panel.x + 16, self.top_panel.y + 76))
        surface.blit(room_label, room_rect)

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

    def _draw_cards(self, surface: pygame.Surface) -> None:
        enabled = self.resolve_timer <= 0 and self.player.hp > 0

        # Requested board layout:
        # pink = deck area, green = room cards, blue = equipped weapon.
        self._draw_slot_outline(surface, self.deck_slot_rect, (255, 63, 206))
        self._draw_slot_outline(surface, self.weapon_slot_rect, (38, 120, 255))
        for slot in self.room_slot_rects:
            self._draw_slot_outline(surface, slot, (49, 245, 70))

        if self.deck.remaining > 0:
            self._draw_card_back(surface, self.deck_slot_rect)
        else:
            empty_label = self.app.card_small_font.render("VAZIO", True, (198, 203, 224))
            empty_rect = empty_label.get_rect(center=self.deck_slot_rect.center)
            surface.blit(empty_label, empty_rect)

        deck_info = self.app.card_small_font.render(
            f"DECK ({self.deck.remaining})",
            True,
            (255, 196, 245),
        )
        deck_info_rect = deck_info.get_rect(midbottom=(self.deck_slot_rect.centerx, self.deck_slot_rect.top - 10))
        surface.blit(deck_info, deck_info_rect)

        equipped_card = self._equipped_weapon_card()
        if equipped_card is not None:
            weapon_face = self.app.assets.get_card_face(equipped_card, self.weapon_slot_rect.size)
            surface.blit(weapon_face, self.weapon_slot_rect)
            icon_size = int(min(self.weapon_slot_rect.width * 0.50, self.weapon_slot_rect.height * 0.34))
            icon_surface = self.app.assets.get_type_icon("weapon", (icon_size, icon_size))
            icon_rect = icon_surface.get_rect(center=(self.weapon_slot_rect.centerx, self.weapon_slot_rect.centery + 4))
            surface.blit(icon_surface, icon_rect)
        else:
            empty = pygame.Surface(self.weapon_slot_rect.size, pygame.SRCALPHA)
            empty.fill((21, 27, 42))
            surface.blit(empty, self.weapon_slot_rect)
            no_weapon = self.app.card_small_font.render("SEM ARMA", True, (187, 198, 224))
            no_weapon_rect = no_weapon.get_rect(center=self.weapon_slot_rect.center)
            surface.blit(no_weapon, no_weapon_rect)

        weapon_info = self.app.card_small_font.render(
            "ESPADA EQUIPADA",
            True,
            (174, 215, 255),
        )
        weapon_info_rect = weapon_info.get_rect(
            midtop=(self.weapon_slot_rect.centerx, self.weapon_slot_rect.bottom + 10)
        )
        surface.blit(weapon_info, weapon_info_rect)

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

        header = self.app.small_font.render("LOG", True, ACCENT_COLOR)
        surface.blit(header, (self.log_panel.x + 14, self.log_panel.y + 8))

        y = self.log_panel.y + 40
        if not self.logs:
            empty = self.app.card_small_font.render("Sem eventos.", True, SUBTEXT_COLOR)
            surface.blit(empty, (self.log_panel.x + 14, y))
            return

        max_lines = 3
        for line in list(self.logs)[:max_lines]:
            label = self.app.card_small_font.render(line, True, TEXT_COLOR)
            surface.blit(label, (self.log_panel.x + 14, y))
            y += 20

        tip = self.app.card_small_font.render(
            "Click esq monstro=arma | dir=mao nua | R reinicia | F11 fullscreen",
            True,
            SUBTEXT_COLOR,
        )
        tip_rect = tip.get_rect(midright=(self.log_panel.right - 14, self.log_panel.y + 20))
        surface.blit(tip, tip_rect)
