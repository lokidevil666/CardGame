from __future__ import annotations

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

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.title_font = pygame.font.SysFont("arial", 40, bold=True)
        self.body_font = pygame.font.SysFont("arial", 28)
        self.small_font = pygame.font.SysFont("arial", 22)
        self.assets = GameAssets()

        self.scene: BaseScene = MenuScene(self)

    def change_scene(self, scene_name: str, **kwargs: object) -> None:
        if scene_name == "menu":
            self.scene = MenuScene(self)
            return
        if scene_name == "combat":
            self.scene = CombatScene(self)
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
                else:
                    self.scene.handle_event(event)

            self.scene.update(dt)
            self.scene.render(self.screen)
            pygame.display.flip()

        self.screen.fill(BG_COLOR)
        pygame.display.flip()
        pygame.quit()
