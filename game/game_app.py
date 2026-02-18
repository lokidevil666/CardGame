from __future__ import annotations

import secrets

import pygame

from game.constants import BG_COLOR, FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from game.scenes.base_scene import BaseScene
from game.scenes.combat_scene import CombatScene
from game.scenes.end_scene import EndScene
from game.scenes.menu_scene import MenuScene
from game.systems.assets import GameAssets


class GameApp:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Scoundrel Roguelike")

        self.window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.is_fullscreen = True
        self.screen = self._build_display()
        self.screen_width, self.screen_height = self.screen.get_size()

        self.clock = pygame.time.Clock()
        self.running = True

        self.title_font = pygame.font.SysFont("arial", 40, bold=True)
        self.body_font = pygame.font.SysFont("arial", 28)
        self.small_font = pygame.font.SysFont("arial", 22)
        self.card_title_font = pygame.font.SysFont("arial", 20, bold=True)
        self.card_small_font = pygame.font.SysFont("arial", 16, bold=True)

        try:
            pygame.scrap.init()
        except pygame.error:
            pass

        self.assets = GameAssets()
        self.current_seed: str = ""

        self.scene: BaseScene = MenuScene(self)

    def _build_display(self) -> pygame.Surface:
        if self.is_fullscreen:
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        return pygame.display.set_mode(self.window_size, pygame.RESIZABLE)

    def toggle_fullscreen(self) -> None:
        self.is_fullscreen = not self.is_fullscreen
        self.screen = self._build_display()
        self.screen_width, self.screen_height = self.screen.get_size()

    def start_new_run(self, seed_text: str | None = None) -> None:
        chosen_seed = (seed_text or "").strip()
        if not chosen_seed:
            chosen_seed = str(secrets.randbelow(10**12))
        self.current_seed = chosen_seed
        self.change_scene("combat", seed=chosen_seed)

    def copy_text(self, text: str) -> bool:
        if not text:
            return False
        try:
            if not pygame.scrap.get_init():
                pygame.scrap.init()
            pygame.scrap.put(pygame.SCRAP_TEXT, text.encode("utf-8"))
            return True
        except (pygame.error, TypeError):
            return False

    def copy_current_seed(self) -> bool:
        return self.copy_text(self.current_seed)

    def change_scene(self, scene_name: str, **kwargs: object) -> None:
        if scene_name == "menu":
            self.scene = MenuScene(self)
            return
        if scene_name == "combat":
            self.scene = CombatScene(self, **kwargs)
            return
        if scene_name == "end":
            self.scene = EndScene(self, **kwargs)
            return
        raise ValueError(f"Unknown scene '{scene_name}'")

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.type == pygame.VIDEORESIZE and not self.is_fullscreen:
                    self.window_size = (event.w, event.h)
                    self.screen = self._build_display()
                    self.screen_width, self.screen_height = self.screen.get_size()
                else:
                    self.scene.handle_event(event)

            self.scene.update(dt)
            self.scene.render(self.screen)
            pygame.display.flip()

        self.screen.fill(BG_COLOR)
        pygame.display.flip()
        pygame.quit()
