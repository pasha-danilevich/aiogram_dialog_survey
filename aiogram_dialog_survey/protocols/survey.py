from abc import abstractmethod
from typing import List, Optional, Protocol, Type

from aiogram_dialog import Dialog
from aiogram_dialog.dialog import OnDialogEvent, OnResultEvent

from aiogram_dialog_survey.entities.question import Question
from aiogram_dialog_survey.protocols.handler import HandlerProtocol
from aiogram_dialog_survey.protocols.state_manager import StateManagerProtocol
from aiogram_dialog_survey.widget_factory import WidgetFactory


class SurveyProtocol(Protocol):
    name: str
    use_numbering: bool
    questions: List['Question']
    state_manager: 'StateManagerProtocol'

    @abstractmethod
    def __init__(
        self,
        name: str,
        questions: list[Question],
        use_numbering: bool,
        handler: Type['HandlerProtocol'],
        state_manager: Type[StateManagerProtocol],
        widget_factory: Type[WidgetFactory],
    ): ...

    @abstractmethod
    def to_dialog(
        self,
        on_start: Optional['OnDialogEvent'] = None,
        on_close: Optional['OnDialogEvent'] = None,
        on_process_result: Optional['OnResultEvent'] = None,
    ) -> 'Dialog': ...
