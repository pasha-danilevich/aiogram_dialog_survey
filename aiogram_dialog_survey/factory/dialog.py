from typing import List, Optional, Type

from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.dialog import OnDialogEvent, OnResultEvent
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Next,
    Row,
)
from aiogram_dialog.widgets.text import Const, Format

from db.tables.questionnaire import QuestionType
from aiogram_dialog_survey import widgets
from aiogram_dialog_survey.factory.state import StateGroupFactory
from aiogram_dialog_survey.handler import WindowHandler
from aiogram_dialog_survey.interface import ActionType, IWindowHandler, QuestionDict


class WrapperWindows:
    state_generator = StateGroupFactory
    start_message = "Header. Начальное сообщение"
    end_message = "Анкета заполнена успешно"

    @classmethod
    def get_start_window(cls, state: Type[StatesGroup]) -> Window:
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
    def get_end_window(cls, state: Type[StatesGroup]) -> Window:
        window = Window(
            Format(cls.end_message),
            Cancel(Const("Отлично, закрыть")),
            state=getattr(state, cls.state_generator.last_state_name),
        )
        return window


async def some_process(manager: DialogManager, key: str):
    print(f'some_process {manager} {key}')


class QuestionnaireFactory(StateGroupFactory, WrapperWindows):
    # TODO: Нужно предусмотреть возможность суб анкет. То есть может появиться ветвление, которое ведет в суб анкету
    def __init__(
        self,
        questionnaire_name: str,
        questions: list[QuestionDict],
        handler: Type[IWindowHandler] = WindowHandler,
    ):
        self._handler = handler
        self.questions = questions
        self.questionnaire_name = questionnaire_name
        self.state_group_name = questionnaire_name.title()
        self._state_group = self.create_state_group(
            self.state_group_name,
            [question["name"] for question in questions],
        )

    @staticmethod
    def _resolve_widget(question_type: QuestionType) -> Type[widgets.Widget]:
        match question_type:
            case QuestionType.MULTISELECT:
                return widgets.Multiselect
            case QuestionType.SELECT:
                return widgets.Select
            case QuestionType.TEXT:
                return widgets.Text

        raise ValueError("Unknown question type")

    

    @staticmethod
    def _get_skip_button(question: QuestionDict, handler: IWindowHandler) -> Button:
        skip_button = (
            Button(
                Const("Пропустить вопрос"),
                id=f'skip_{question["name"]}',
                on_click=handler.get_handler(ActionType.ON_SKIP),
            )
            if not question["is_required"]
            else (Const(''))  # пустая кнопка, не будет отображаться
        )
        return skip_button

    def _wrap_windows(self, windows: List[Window]) -> List[Window]:
        windows.insert(0, self.get_start_window(self._state_group))
        windows.append(self.get_end_window(self._state_group))
        return windows
    
    def create_windows(self) -> List[Window]:
        windows = list()
        questionnaire_length = len(self.questions)

        for order, question in enumerate(self.questions):
            handler = self._handler(question_name=question["name"])
            widget = self._resolve_widget(question["question_type"])

            window = Window(
                Const(f"Вопрос {order + 1}/{questionnaire_length}"),
                Const(f"{question['text']}"),
                widget(question, handler).create(),
                Row(
                    Cancel(Const("Отменить заполнение")),
                    Back(Const("Назад")),
                ),
                self._get_skip_button(question, handler),
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
        windows = self._wrap_windows(self.create_windows())
        return Dialog(
            *windows,
            on_start=on_start,
            on_close=on_close,
            on_process_result=on_process_result,
        )

    def get_first_state(self) -> State:
        state_attributes = {
            name: value
            for name, value in vars(self._state_group).items()
            if isinstance(value, State)
        }
        first_state_name = next(iter(state_attributes))
        first_state_value = state_attributes[first_state_name]
        return first_state_value
