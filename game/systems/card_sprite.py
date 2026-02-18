from __future__ import annotations

from dataclasses import dataclass

import pygame

from game.constants import CARD_COLORS, CARD_HEIGHT, CARD_WIDTH, TEXT_COLOR
from game.models.card import Card


def _lerp(current: float, target: float, speed: float, dt: float) -> float:
    if abs(current - target) < 0.001:
        return target
    return current + (target - current) * min(1.0, speed * dt)


@dataclass(slots=True)
class CardSprite:
    card: Card
    center_x: float
    center_y: float
    width: int = CARD_WIDTH
    height: int = CARD_HEIGHT
    base_scale: float = 1.0
    scale: float = 1.0
    lift: float = 0.0
    hovered: bool = False
    is_resolving: bool = False
    click_timer: float = 0.0

    def _rect_for_draw(self) -> pygame.Rect:
        click_scale = 0.92 if self.click_timer > 0.10 else 1.0
        final_scale = self.scale * click_scale
        draw_w = int(self.width * final_scale)
        draw_h = int(self.height * final_scale)
        center_y = int(self.center_y - self.lift)
        return pygame.Rect(
            int(self.center_x - draw_w / 2),
            int(center_y - draw_h / 2),
            draw_w,
            draw_h,
        )

    @property
    def interaction_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.center_x - self.width / 2),
            int(self.center_y - self.height / 2),
            self.width,
            self.height,
        )

    def update(self, dt: float, mouse_pos: tuple[int, int], can_interact: bool) -> None:
        self.hovered = can_interact and self.interaction_rect.collidepoint(mouse_pos)
        target_scale = self.base_scale * (1.08 if self.hovered else 1.0)
        target_lift = 18.0 if self.hovered else 0.0
        self.scale = _lerp(self.scale, target_scale, speed=15.0, dt=dt)
        self.lift = _lerp(self.lift, target_lift, speed=14.0, dt=dt)

        if self.click_timer > 0:
            self.click_timer = max(0.0, self.click_timer - dt)

    def contains(self, pos: tuple[int, int]) -> bool:
        return self.interaction_rect.collidepoint(pos)

    def trigger_click(self) -> None:
        self.click_timer = 0.16

    def draw(
        self,
        surface: pygame.Surface,
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
        small_font: pygame.font.Font,
        enabled: bool,
    ) -> None:
        rect = self._rect_for_draw()

        color = CARD_COLORS[self.card.card_type]
        if self.hovered and enabled:
            color = tuple(min(255, channel + 25) for channel in color)
        if not enabled:
            color = tuple(max(50, channel - 30) for channel in color)

        shadow_rect = rect.move(0, 8)
        pygame.draw.rect(surface, (8, 10, 15), shadow_rect, border_radius=16)
        pygame.draw.rect(surface, color, rect, border_radius=16)
        pygame.draw.rect(surface, (16, 17, 24), rect, width=3, border_radius=16)

        short_label = title_font.render(self.card.short_name, True, TEXT_COLOR)
        short_label_rect = short_label.get_rect(midtop=(rect.centerx, rect.top + 18))
        surface.blit(short_label, short_label_rect)

        type_label = body_font.render(self.card.card_type.upper(), True, TEXT_COLOR)
        type_label_rect = type_label.get_rect(center=(rect.centerx, rect.centery - 6))
        surface.blit(type_label, type_label_rect)

        value_label = title_font.render(str(self.card.value), True, TEXT_COLOR)
        value_label_rect = value_label.get_rect(center=(rect.centerx, rect.centery + 42))
        surface.blit(value_label, value_label_rect)

        if self.card.card_type == "monster":
            desc = "Dano base"
        elif self.card.card_type == "potion":
            desc = "Cura HP"
        else:
            desc = "Poder da espada"
        desc_label = small_font.render(desc, True, TEXT_COLOR)
        desc_rect = desc_label.get_rect(midbottom=(rect.centerx, rect.bottom - 14))
        surface.blit(desc_label, desc_rect)
