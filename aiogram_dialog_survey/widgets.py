# widgets.py
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Type, Union

from aiogram import F
from aiogram.fsm.state import State
from aiogram.types import Message
from aiogram_dialog.api.entities import Data, ShowMode, StartMode
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.input import TextInput as AiogramTextInput
from aiogram_dialog.widgets.kbd import Button as AiogramDialogButton
from aiogram_dialog.widgets.kbd import Column
from aiogram_dialog.widgets.kbd import Multiselect as AiogramDialogMultiselect
from aiogram_dialog.widgets.kbd import Select as AiogramDialogSelect
from aiogram_dialog.widgets.kbd import Start as AiogramDialogStart
from aiogram_dialog.widgets.kbd.button import OnClick
from aiogram_dialog.widgets.text import Const, Format, Text

from aiogram_dialog_survey.interface import (
    AbstractValidator,
    ActionType,
    IWindowHandler,
    Question,
    QuestionType,
)

WidgetButton = Tuple[str, Union[str, int]]


class Widget(ABC):
    @abstractmethod
    def __init__(self, question: Question, handler: IWindowHandler):
        pass

    @abstractmethod
    def create(self):
        pass


class BaseWidget(Widget):
    def __init__(self, question: Question, handler: IWindowHandler):
        self.question = question
        self.handler = handler

    def create(self):
        raise NotImplementedError

    @property
    def item_id_getter(self):
        return lambda x: x[1]

    def create_buttons(self) -> list[WidgetButton]:
        return [(button.text, button.callback) for button in self.question.buttons]


class TextInput(BaseWidget):
    def create(self):
        return AiogramTextInput(
            id=f'input_{self.question.name.strip()}',
            on_success=self.handler.get_handler(ActionType.ON_INPUT_SUCCESS),
            type_factory=self.question.validator.type_factory,
            on_error=self.question.validator.on_error,
        )


class Select(BaseWidget):
    def create(self):
        return Column(
            AiogramDialogSelect(
                text=Format("{item[0]}"),
                id=f'select_{self.question.name.strip()}',
                item_id_getter=self.item_id_getter,
                items=self.create_buttons(),
                on_click=self.handler.get_handler(
                    ActionType.ON_SELECT
                ),  # используем partial
            )
        )


class Multiselect(BaseWidget):
    ACCEPT_BUTTON_TEXT = "Подтвердить выбор"

    def create(self):
        return Column(
            AiogramDialogMultiselect(
                Format("✓ {item[0]}"),  # Selected item format
                Format("{item[0]}"),  # Unselected item format
                id=f'multi_{self.question.name.strip()}',
                item_id_getter=self.item_id_getter,
                items=self.create_buttons(),
                on_click=self.handler.get_handler(ActionType.ON_MULTISELECT),
            ),
            AiogramDialogButton(
                Const(self.ACCEPT_BUTTON_TEXT),
                id='__accept__',
                on_click=self.handler.get_handler(ActionType.ON_ACCEPT),
                when=F["dialog_data"][self.handler.get_widget_key()].len()
                > 0,  # Only show when items are selected
            ),
        )


class WidgetManager:
    @staticmethod
    def get_widget(question_type: QuestionType) -> Type[Widget]:
        match question_type:
            case QuestionType.MULTISELECT:
                return Multiselect
            case QuestionType.SELECT:
                return Select
            case QuestionType.TEXT:
                return TextInput

        raise ValueError("Unknown question type")

    @staticmethod
    def get_skip_button(
        question: Question, handler: IWindowHandler
    ) -> AiogramDialogButton | Const:
        if not question.is_required:
            return AiogramDialogButton(
                Const("Пропустить вопрос"),
                id=f'skip_{question.name.strip()}',
                on_click=handler.get_handler(ActionType.ON_SKIP),
            )
        return AiogramDialogButton(Const(''), id='empty')  # пустая кнопка

    @staticmethod
    def get_start_button(text: str, state: State) -> AiogramDialogStart:
        return AiogramDialogStart(Const(text), id='start_survey', state=state)


class StartSurvey(AiogramDialogStart):
    def __init__(
        self,
        text: Text,
        survey: 'Survey',
        id: str = "survey",
        data: Data = None,
        on_click: Optional[OnClick] = None,
        show_mode: Optional[ShowMode] = None,
        mode: StartMode = StartMode.NORMAL,
        when: WhenCondition = None,
    ):
        super().__init__(
            text=text,
            id=id,
            state=survey.state_manager.get_first_state(),
            data=data,
            on_click=on_click,
            show_mode=show_mode,
            mode=mode,
            when=when,
        )


class Validator(AbstractValidator):
    @staticmethod
    async def on_error(message: Message, _, __, error: ValueError):
        await message.answer(str(error))
