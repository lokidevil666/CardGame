from __future__ import annotations

from abc import ABC, abstractmethod

import pygame


class BaseScene(ABC):
    def __init__(self, app: "GameApp") -> None:
        self.app = app

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self, dt: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        raise NotImplementedError
