from typing import Protocol

from aiogram_dialog_survey.entities.question import Question
from aiogram_dialog_survey.protocols.handler import HandlerProtocol


class WidgetProtocol(Protocol):
    def render(self, question: Question, handler: HandlerProtocol):
        raise NotImplementedError
