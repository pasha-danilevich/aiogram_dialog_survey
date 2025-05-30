from typing import List, Optional, Type

from aiogram_dialog import Dialog, Window
from aiogram_dialog.dialog import OnDialogEvent, OnResultEvent
from aiogram_dialog.widgets.kbd import (
    Back,
    Cancel,
    Row,
)
from aiogram_dialog.widgets.text import Const

from aiogram_dialog_survey.handler import WindowHandler
from aiogram_dialog_survey.interface import IWindowHandler, QuestionDict
from aiogram_dialog_survey.state import StateManager
from aiogram_dialog_survey.widgets import WidgetManager
from aiogram_dialog_survey.window import Wrapper


class Survey:
    def __init__(
        self,
        name: str,
        questions: list[QuestionDict],
        handler: Type[IWindowHandler] = WindowHandler,
        wrapper: Type[Wrapper] = Wrapper,
        state_manager: Type[StateManager] = StateManager,
        widget_manager: Type[WidgetManager] = WidgetManager,
    ):
        self.name = name
        self._handler = handler
        self.questions = questions
        self.wrapper = wrapper()
        self.state_manager = state_manager(name=name, questions=questions)
        self.widget_manager = widget_manager
        self._state_group = self.state_manager.state_group

    def to_dialog(
        self,
        on_start: Optional[OnDialogEvent] = None,
        on_close: Optional[OnDialogEvent] = None,
        on_process_result: Optional[OnResultEvent] = None,
    ) -> Dialog:
        windows = self.wrapper.wrap_windows(self._create_windows(), self._state_group)
        return Dialog(
            *windows,
            on_start=on_start,
            on_close=on_close,
            on_process_result=on_process_result,
        )

    def _create_windows(self) -> List[Window]:
        windows = list()
        questionnaire_length = len(self.questions)

        for order, question in enumerate(self.questions):
            handler = self._handler(question_name=question["name"])
            widget = self.widget_manager.get_widget(question["question_type"])

            window = Window(
                Const(f"Вопрос {order + 1}/{questionnaire_length}"),
                Const(f"{question['text']}"),
                widget(question, handler).create(),
                Row(
                    Cancel(Const("Отменить заполнение")),
                    Back(Const("Назад")),
                ),
                self.widget_manager.get_skip_button(question, handler),
                state=getattr(self._state_group, question["name"]),
            )
            windows.append(window)

        return windows
