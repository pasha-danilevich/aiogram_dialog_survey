from abc import abstractmethod
from enum import StrEnum
from typing import Awaitable, Callable, List, Protocol, TypedDict, Union, Optional

from aiogram_dialog import DialogManager

from db.tables.questionnaire import QuestionType

QuestionnaireName = str

QuestionName = str

ProcessHandler = Callable[[DialogManager, QuestionName], Awaitable[None]]


class Button(TypedDict):
    text: str
    id: Union[int, str]


class QuestionDict(TypedDict):
    id: int
    name: str
    question_type: QuestionType
    text: str
    is_required: bool
    options: Optional[List[Button]]


class ActionType(StrEnum):
    ON_SELECT = "on_select"
    ON_INPUT_SUCCESS = "on_input_success"
    ON_MULTISELECT = "on_multiselect"

    ON_ACCEPT = "on_accept"
    ON_SKIP = "on_skip"


class IWindowHandler(Protocol):
    @abstractmethod
    def __init__(self, question_name: str):
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
    @abstractmethod
    async def end_handler(manager: DialogManager):
        pass
