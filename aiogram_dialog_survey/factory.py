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
from aiogram_dialog_survey.state import StateGroupManager
from aiogram_dialog_survey.widgets import WidgetManager
from aiogram_dialog_survey.window import Wrapper


class SurveyFactory(Wrapper, StateGroupManager, WidgetManager):
    # TODO: Нужно предусмотреть возможность суб анкет. То есть может появиться ветвление, которое ведет в суб анкету
    def __init__(
        self,
        name: str,
        questions: list[QuestionDict],
        handler: Type[IWindowHandler] = WindowHandler,
    ):
        super().__init__(name, questions)
        self._handler = handler
        self.questions = questions
        self._wrapper = None
        self._state_group = self.create_state_group(
            name.title(),
            [question["name"] for question in questions],
        )

    def create_windows(self) -> List[Window]:
        windows = list()
        questionnaire_length = len(self.questions)

        for order, question in enumerate(self.questions):
            handler = self._handler(question_name=question["name"])
            widget = self.get_widget(question["question_type"])

            window = Window(
                Const(f"Вопрос {order + 1}/{questionnaire_length}"),
                Const(f"{question['text']}"),
                widget(question, handler).create(),
                Row(
                    Cancel(Const("Отменить заполнение")),
                    Back(Const("Назад")),
                ),
                self.get_skip_button(question, handler),
                state=getattr(self._state_group, question["name"]),
            )
            windows.append(window)

        return windows

    def to_dialog(
        self,
        on_start: Optional[OnDialogEvent] = None,
        on_close: Optional[OnDialogEvent] = None,
        on_process_result: Optional[OnResultEvent] = None,
    ) -> Dialog:
        windows = self.wrap_windows(self.create_windows(), self._state_group)
        return Dialog(
            *windows,
            on_start=on_start,
            on_close=on_close,
            on_process_result=on_process_result,
        )
