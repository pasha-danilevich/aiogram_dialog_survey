from typing import Protocol
from aiogram_dialog.widgets.kbd import Button

class NavigationButtonProtocol(Protocol):
    def render(self, order: int) -> list[Button]:
        pass