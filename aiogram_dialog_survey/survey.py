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

from aiogram_dialog_survey.entities.question import Question
from aiogram_dialog_survey.handler import WindowHandler
from aiogram_dialog_survey.protocols.handler import HandlerProtocol
from aiogram_dialog_survey.protocols.state_manager import StateManagerProtocol
from aiogram_dialog_survey.protocols.survey import SurveyProtocol
from aiogram_dialog_survey.protocols.widget import WidgetProtocol
from aiogram_dialog_survey.protocols.widget_factory import WidgetFactoryProtocol
from aiogram_dialog_survey.state import StateManager
from aiogram_dialog_survey.widget_factory import WidgetFactory


class Survey(SurveyProtocol):
    def __init__(
        self,
        name: str,
        questions: list[Question],
        use_numbering: bool = True,
        handler: Type[HandlerProtocol] = WindowHandler,
        state_manager: Type[StateManagerProtocol] = StateManager,
        widget_factory: Type[WidgetFactoryProtocol] = WidgetFactory,
    ):
        if len(questions) == 0:
            raise ValueError("Список вопросов не может быть пустым")

        self.name = name
        self.use_numbering = use_numbering
        self.questions = questions
        self.state_manager = state_manager(name=name, questions=questions)
        self._widget_factory = widget_factory
        self._handler = handler

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

    def register_widget(self, widget_cls: WidgetProtocol):
        self._widget_factory.register(widget_cls)

    @staticmethod
    def _render_navigation_buttons(order: int) -> list[Button]:
        buttons = []

        if order == 0:
            pass
        else:
            buttons.append(Back(Const("Назад")))

        buttons.append(Cancel(Const("Отменить заполнение")))

        return buttons

    def _create_windows(self) -> List[Window]:
        windows = list()
        questions_count = len(self.questions)

        for order, question in enumerate(self.questions):
            handler = self._handler(survey=self, question=question)
            sequence_question_label = (
                Const(f"Вопрос {order + 1}/{questions_count}")
                if self.use_numbering
                else Const("")
            )
            widget = self._widget_factory.create(question.widget_type)
            skip_button = self._widget_factory.create("SkipButton")

            window = Window(
                sequence_question_label,
                Const(f"{question.text}"),
                widget.render(question, handler),
                Group(
                    *[
                        *self._render_navigation_buttons(order),
                        skip_button.render(question, handler),
                    ],
                    width=2,
                ),
                state=self.state_manager.get_by_name(question.name),
            )

            windows.append(window)

        return windows
