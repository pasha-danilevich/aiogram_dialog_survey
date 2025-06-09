from abc import abstractmethod
from typing import Protocol, TypeAlias

from aiogram_dialog import Data, DialogManager

from aiogram_dialog_survey.entities.action_type import ActionType
from aiogram_dialog_survey.entities.question import Question

QuestionName: TypeAlias = str


class HandlerProtocol(Protocol):
    @abstractmethod
    def __init__(self, survey: 'SurveyProtocol', question: Question):
        raise NotImplementedError

    @abstractmethod
    def get_widget_key(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_handler(self, handler_type: ActionType):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def process_handler(
        manager: DialogManager, widget_key: QuestionName, action_type: ActionType
    ) -> None:
        """Запускается при каждом действии в каждом окне. Переопределите данный метод для внедрения собственной логики"""
        raise NotImplementedError

    @staticmethod
    async def process_survey_result(manager: DialogManager, result: Data) -> None:
        """Функция запускается в конце анкетирования, после последнего ответа"""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    async def next_or_done(manager: DialogManager):
        raise NotImplementedError
