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
from aiogram_dialog_survey.interface import IWindowHandler, QuestionDict
from aiogram_dialog_survey.state import StateManager
from aiogram_dialog_survey.widgets import WidgetManager
from aiogram_dialog_survey.window import Wrapper


class Survey:
    def __init__(
        self,
        name: str,
        questions: list[QuestionDict],
        is_subdialog: bool = False,
        handler: Type[IWindowHandler] = WindowHandler,
        wrapper: Type[Wrapper] = Wrapper,
        state_manager: Type[StateManager] = StateManager,
        widget_manager: Type[WidgetManager] = WidgetManager,
    ):
        self.name = name
        self.is_subdialog = is_subdialog
        self._handler = handler
        self.questions = questions
        self.wrapper = wrapper()
        self.state_manager = state_manager(
            name=name, questions=questions, use_wrapper=not is_subdialog
        )
        self.widget_manager = widget_manager
        self._state_group = self.state_manager.state_group

    def to_dialog(
        self,
        on_start: Optional[OnDialogEvent] = None,
        on_close: Optional[OnDialogEvent] = None,
        on_process_result: Optional[OnResultEvent] = None,
    ) -> Dialog:
        if self.is_subdialog:
            windows = self._create_windows()
        else:
            windows = self.wrapper.wrap_windows(
                self._create_windows(), self._state_group
            )

        return Dialog(
            *windows,
            on_start=on_start,
            on_close=on_close,
            on_process_result=on_process_result,
        )

    def _get_static_buttons(self, order: int) -> list[Button]:
        buttons = []
        back_text = Const("Назад")
        cancel_text = Const("Отменить заполнение")

        if self.is_subdialog:
            if order == 0:
                buttons.append(Cancel(back_text))
            else:
                buttons.append(Back(back_text))
        else:
            buttons.append(Cancel(cancel_text))
            buttons.append(Back(back_text))

        return buttons

    def _create_windows(self) -> List[Window]:
        windows = list()
        questionnaire_length = len(self.questions)

        for order, question in enumerate(self.questions):
            handler = self._handler(question_name=question["name"])
            sequence_question_label = (
                Const("")
                if self.is_subdialog
                else Const(f"Вопрос {order + 1}/{questionnaire_length}")
            )
            widget = self.widget_manager.get_widget(question["question_type"])
            static_buttons = self._get_static_buttons(order)

            window = Window(
                sequence_question_label,
                Const(f"{question['text']}"),
                widget(question, handler).create(),
                Group(
                    *[
                        *static_buttons,
                        self.widget_manager.get_skip_button(question, handler),
                    ],
                    width=2,
                ),
                state=getattr(self._state_group, question["name"]),
            )

            windows.append(window)

        return windows
