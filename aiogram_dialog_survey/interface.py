# interface.py
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Awaitable, Callable, List, Optional, Protocol, TypeVar

from aiogram.types import Message
from aiogram_dialog import DialogManager, Data
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

QuestionName = str

ProcessHandler = Callable[[DialogManager, QuestionName], Awaitable[None]]


class QuestionType(StrEnum):
    TEXT = "text"
    SELECT = "select"
    MULTISELECT = "multiselect"


class Button(BaseModel):
    text: str
    callback: str

    @field_validator('callback')
    def validate_byte_size(cls, v: str) -> str:
        byte_size = len(v.encode('utf-8'))
        if byte_size > 64:
            raise ValueError(
                f"Размер поля превышает 64 байта (текущий размер: {byte_size} байт)"
            )
        return v


T = TypeVar("T")
TypeFactory = Callable[[str], T]


class AbstractValidator(ABC):
    def __init__(self, type_factory: TypeFactory):
        self.type_factory = type_factory

    @staticmethod
    @abstractmethod
    async def on_error(message: Message, _, __, error: ValueError):
        pass


class StringValidator(AbstractValidator):
    def __init__(self, type_factory: TypeFactory = str):
        super().__init__(type_factory)
    
    @staticmethod
    async def on_error(message: Message, _, __, error: ValueError):
        pass

class Question(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    question_type: QuestionType
    text: str
    is_required: bool
    buttons: Optional[List[Button]] = None
    validator: Optional[AbstractValidator] = StringValidator()

    @model_validator(mode='after')
    def validate_buttons_based_on_type(self) -> 'Question':
        if self.question_type == QuestionType.TEXT:
            if self.buttons:
                raise ValueError("Для TEXT-вопроса кнопки не допускаются")
        elif self.question_type in (QuestionType.SELECT, QuestionType.MULTISELECT):
            if not self.buttons or len(self.buttons) == 0:
                raise ValueError(
                    f"Для {self.question_type.value.upper()}-вопроса обязательны кнопки"
                )
            if len(self.buttons) < 2:
                raise ValueError(
                    f"Для {self.question_type.value.upper()}-вопроса нужно минимум 2"
                    " кнопки"
                )
        return self

    @field_validator('buttons')
    def validate_unique_button_callbacks(
        cls, buttons: Optional[List[Button]]
    ) -> Optional[List[Button]]:
        if buttons:
            button_callbacks = [button.callback for button in buttons]
            if len(button_callbacks) != len(set(button_callbacks)):
                raise ValueError("callback кнопок должны быть уникальными")
        return buttons


class ActionType(StrEnum):
    ON_SELECT = "on_select"
    ON_INPUT_SUCCESS = "on_input_success"
    ON_MULTISELECT = "on_multiselect"

    ON_ACCEPT = "on_accept"
    ON_SKIP = "on_skip"

class ISurvey(Protocol):
    pass

class IWindowHandler(Protocol):
    @abstractmethod
    def __init__(self, survey: ISurvey, question: Question):
        pass

    @abstractmethod
    def get_widget_key(self) -> str:
        pass

    @abstractmethod
    def get_handler(self, handler_type: ActionType):
        pass

    @staticmethod
    @abstractmethod
    async def process_handler(
        manager: DialogManager, widget_key: QuestionName, action_type: ActionType
    ) -> None:
        """Запускается при каждом действии в каждом окне. Переопределите данный метод для внедрения собственной логики"""
    
    @staticmethod
    async def process_survey_result(
        manager: DialogManager, result: Data
    ) -> None:
        """Функция запускается в конце анкетирования, после последнего ответа"""

    @staticmethod
    @abstractmethod
    async def next_or_done(manager: DialogManager):
        pass
