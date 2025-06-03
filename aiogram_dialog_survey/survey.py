# survey.py
from typing import List, Optional, Type

from aiogram_dialog import Dialog, Window
from aiogram_dialog.dialog import OnDialogEvent, OnResultEvent
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Group,
)
from aiogram_dialog.widgets.text import Const

from aiogram_dialog_survey.handler import WindowHandler
from aiogram_dialog_survey.interface import IWindowHandler, Question, ISurvey
from aiogram_dialog_survey.state import StateManager
from aiogram_dialog_survey.widgets import WidgetManager


class Survey(ISurvey):
    def __init__(
        self,
        name: str,
        questions: list[Question],
        use_numbering: bool = True,
        handler: Type[IWindowHandler] = WindowHandler,
        state_manager: Type[StateManager] = StateManager,
        widget_manager: Type[WidgetManager] = WidgetManager,
    ):
        self.name = name
        self.use_numbering = use_numbering
        self._handler = handler
        self.questions = questions
        self.state_manager = state_manager(name=name, questions=questions)
        self.widget_manager = widget_manager
        self._state_group = self.state_manager.state_group

    def to_dialog(
        self,
        on_start: Optional[OnDialogEvent] = None,
        on_close: Optional[OnDialogEvent] = None,
        on_process_result: Optional[OnResultEvent] = None,
    ) -> Dialog:
        return Dialog(
            *self._create_windows(),
            on_start=on_start,
            on_close=on_close,
            on_process_result=on_process_result,
        )

    @staticmethod
    def _get_static_buttons(order: int) -> list[Button]:
        buttons = []

        if order == 0:
            buttons.append(Cancel(Const("Назад")))
        else:
            buttons.append(Back(Const("Назад")))

        buttons.append(Cancel(Const("Отменить заполнение")))

        return buttons

    def _create_windows(self) -> List[Window]:
        windows = list()
        questionnaire_length = len(self.questions)

        for order, question in enumerate(self.questions):
            handler = self._handler(survey=self, question=question)
            sequence_question_label = (
                Const(f"Вопрос {order + 1}/{questionnaire_length}")
                if self.use_numbering
                else Const("")
            )
            widget = self.widget_manager.get_widget(question.question_type)
            static_buttons = self._get_static_buttons(order)

            window = Window(
                sequence_question_label,
                Const(f"{question.text}"),
                widget(question, handler).create(),
                Group(
                    *[
                        *static_buttons,
                        self.widget_manager.get_skip_button(question, handler),
                    ],
                    width=2,
                ),
                state=getattr(self._state_group, question.name),
            )

            windows.append(window)

        return windows
