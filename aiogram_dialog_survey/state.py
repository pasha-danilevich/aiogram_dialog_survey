# state.py
from typing import List, Type

from aiogram.fsm.state import State, StatesGroup

from aiogram_dialog_survey.entities.question import Question
from aiogram_dialog_survey.protocols.state_manager import StateManagerProtocol


class StateManager(StateManagerProtocol):
    def __init__(self, name: str, questions: list[Question]):
        self.state_group = self._create_state_group(
            name.title(),
            [question.name for question in questions],
        )

    @classmethod
    def _create_state_group(
        cls, group_name: str, state_names: List[str]
    ) -> Type[StatesGroup]:
        """
        Динамически создает класс StatesGroup с заданными состояниями.

        :param group_name: Имя класса StatesGroup.
        :param state_names: Список имен состояний.
        :return: Класс, унаследованный от StatesGroup.
        """

        attrs = {name: State() for name in state_names}

        # Создаем сам класс с помощью type()
        state_group = type(group_name, (StatesGroup,), attrs)

        return state_group  # type: ignore

    def get_first_state(self) -> State:
        state_attributes = {
            name: value
            for name, value in vars(self.state_group).items()
            if isinstance(value, State)
        }
        first_state_name = next(iter(state_attributes))
        return state_attributes[first_state_name]

    def get_by_name(self, name: str) -> State:
        return getattr(self.state_group, name)

    def get_by_index(self, index: int) -> State:
        return list(self.state_group)[index]
