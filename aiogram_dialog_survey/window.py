from typing import Type

from aiogram.fsm.state import StatesGroup
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import (
    Cancel,
    Next,
    Row,
)
from aiogram_dialog.widgets.text import Const, Format

from aiogram_dialog_survey.state import StateGroupFactory


class Wrapper:
    state_generator = StateGroupFactory
    start_message = "Заполните, пожалуйста, анкету"
    end_message = "Анкета заполнена успешно"

    @classmethod
    def _get_start_window(cls, state: Type[StatesGroup]) -> Window:
        window = Window(
            Format(cls.start_message),
            Row(
                Cancel(Const("Закрыть")),
                Next(Const("Продолжить")),
            ),
            state=getattr(state, cls.state_generator.first_state_name),
        )
        return window

    @classmethod
    def _get_end_window(cls, state: Type[StatesGroup]) -> Window:
        window = Window(
            Format(cls.end_message),
            Cancel(Const("Отлично, закрыть")),
            state=getattr(state, cls.state_generator.last_state_name),
        )
        return window

    def wrap_windows(
        self, windows: list[Window], state: Type[StatesGroup]
    ) -> list[Window]:
        windows.insert(0, self._get_start_window(state))
        windows.append(self._get_end_window(state))
        return windows
