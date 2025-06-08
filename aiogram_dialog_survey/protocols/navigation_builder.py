from abc import abstractmethod
from typing import Protocol

from aiogram_dialog_survey.entities.button import Button


class NavigationBuilderProtocol(Protocol):
    @staticmethod
    @abstractmethod
    def get_buttons(order: int) -> list[Button]:
        pass
