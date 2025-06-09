from typing import Protocol, Type

from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog_survey.entities.question import Question


class StateManagerProtocol(Protocol):
    state_group: Type[StatesGroup]

    def __init__(self, name: str, questions: list[Question]): ...

    def get_first_state(self) -> State:
        """
        Возвращает первое состояние из группы состояний.
        """
        ...

    def get_by_name(self, name: str) -> State:
        """
        Возвращает состояние по его имени.
        """
        ...

    def get_by_index(self, index: int) -> State:
        """
        Возвращает состояние по его индексу.
        """
        ...
