from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame

from game.constants import CARD_HEIGHT, CARD_WIDTH
from game.models.card import Card

if TYPE_CHECKING:
    from game.systems.assets import GameAssets


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
    draw_x: float | None = None
    draw_y: float | None = None
    slide_from_x: float = 0.0
    slide_from_y: float = 0.0
    slide_elapsed: float = 0.0
    slide_delay: float = 0.0
    slide_duration: float = 0.32
    is_sliding: bool = False
    entry_pending: bool = False

    def snap_to_target(self) -> None:
        self.draw_x = self.center_x
        self.draw_y = self.center_y
        self.is_sliding = False
        self.entry_pending = False

    def start_slide_from(
        self,
        start_x: float,
        start_y: float,
        *,
        delay: float = 0.0,
        duration: float = 0.32,
    ) -> None:
        self.draw_x = start_x
        self.draw_y = start_y
        self.slide_from_x = start_x
        self.slide_from_y = start_y
        self.slide_delay = max(0.0, delay)
        self.slide_duration = max(0.05, duration)
        self.slide_elapsed = 0.0
        self.is_sliding = True
        self.entry_pending = False

    def _slide_value(self, current: float, start: float, target: float, t: float) -> float:
        _ = current
        eased = 1.0 - (1.0 - t) ** 3
        return start + (target - start) * eased

    def _rect_for_draw(self) -> pygame.Rect:
        click_scale = 0.92 if self.click_timer > 0.10 else 1.0
        final_scale = self.scale * click_scale
        draw_w = int(self.width * final_scale)
        draw_h = int(self.height * final_scale)
        current_x = self.center_x if self.draw_x is None else self.draw_x
        current_y = self.center_y if self.draw_y is None else self.draw_y
        center_y = int(current_y - self.lift)
        return pygame.Rect(
            int(current_x - draw_w / 2),
            int(center_y - draw_h / 2),
            draw_w,
            draw_h,
        )

    @property
    def interaction_rect(self) -> pygame.Rect:
        current_x = self.center_x if self.draw_x is None else self.draw_x
        current_y = self.center_y if self.draw_y is None else self.draw_y
        return pygame.Rect(
            int(current_x - self.width / 2),
            int(current_y - self.height / 2),
            self.width,
            self.height,
        )

    def update(self, dt: float, mouse_pos: tuple[int, int], can_interact: bool) -> None:
        if self.draw_x is None or self.draw_y is None:
            self.draw_x = self.center_x
            self.draw_y = self.center_y

        if self.is_sliding:
            self.slide_elapsed += dt
            effective = self.slide_elapsed - self.slide_delay
            if effective <= 0:
                self.draw_x = self.slide_from_x
                self.draw_y = self.slide_from_y
            else:
                t = min(1.0, effective / self.slide_duration)
                self.draw_x = self._slide_value(self.draw_x, self.slide_from_x, self.center_x, t)
                self.draw_y = self._slide_value(self.draw_y, self.slide_from_y, self.center_y, t)
                if t >= 1.0:
                    self.is_sliding = False
                    self.draw_x = self.center_x
                    self.draw_y = self.center_y
        else:
            self.draw_x = self.center_x
            self.draw_y = self.center_y

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
        detail_font: pygame.font.Font,
        enabled: bool,
        assets: "GameAssets",
    ) -> None:
        rect = self._rect_for_draw()

        shadow_rect = rect.move(0, 8)
        pygame.draw.rect(surface, (8, 10, 15), shadow_rect, border_radius=16)
        card_image = assets.get_card_face(self.card, (rect.width, rect.height))
        surface.blit(card_image, rect)

        icon_size = int(min(rect.width * 0.50, rect.height * 0.34))
        icon_surface = assets.get_type_icon(self.card.card_type, (icon_size, icon_size))
        icon_rect = icon_surface.get_rect(center=(rect.centerx, rect.centery + 4))
        surface.blit(icon_surface, icon_rect)

        if self.card.card_type == "monster":
            desc = "Monstro"
            desc_color = (140, 45, 60)
            detail = f"Dano {self.card.value}"
        elif self.card.card_type == "potion":
            desc = "Pocao"
            desc_color = (38, 125, 82)
            detail = f"Cura {self.card.value}"
        else:
            desc = "Espada"
            desc_color = (54, 86, 154)
            detail = f"Ataque {self.card.value}"

        top_tag = pygame.Rect(0, 0, rect.width - 20, 30)
        top_tag.midtop = (rect.centerx, rect.top + 10)
        pygame.draw.rect(surface, (242, 245, 253), top_tag, border_radius=8)
        pygame.draw.rect(surface, (35, 41, 58), top_tag, width=2, border_radius=8)

        desc_label = title_font.render(desc.upper(), True, desc_color)
        desc_rect = desc_label.get_rect(center=top_tag.center)
        surface.blit(desc_label, desc_rect)

        detail_bg = pygame.Rect(0, 0, rect.width - 20, 34)
        detail_bg.midbottom = (rect.centerx, rect.bottom - 12)
        pygame.draw.rect(surface, (245, 249, 255), detail_bg, border_radius=8)
        pygame.draw.rect(surface, (31, 36, 52), detail_bg, width=2, border_radius=8)

        detail_label = detail_font.render(detail, True, (23, 28, 42))
        detail_rect = detail_label.get_rect(center=detail_bg.center)
        surface.blit(detail_label, detail_rect)

        pygame.draw.rect(surface, (16, 21, 34), rect, width=3, border_radius=16)
        if self.hovered and enabled:
            glow_rect = rect.inflate(8, 8)
            pygame.draw.rect(surface, (133, 193, 255), glow_rect, width=3, border_radius=18)

        if not enabled:
            overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            overlay.fill((18, 21, 31, 120))
            surface.blit(overlay, rect)
