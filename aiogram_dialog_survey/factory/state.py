from typing import List, Type

from aiogram.fsm.state import State, StatesGroup


class StateGroupFactory(StatesGroup):
    first_state_name = "start"
    last_state_name = "end"

    @classmethod
    def create_state_group(
        cls, group_name: str, state_names: List[str]
    ) -> Type[StatesGroup]:
        """
        Динамически создает класс StatesGroup с заданными состояниями.

        :param group_name: Имя класса StatesGroup.
        :param state_names: Список имен состояний.
        :return: Класс, унаследованный от StatesGroup.
        """

        state_names.insert(0, cls.first_state_name)
        state_names.append(cls.last_state_name)

        # Создаем атрибуты класса (состояния) из списка строк
        attrs = {name: State() for name in state_names}

        # Создаем сам класс с помощью type()
        state_group = type(group_name, (StatesGroup,), attrs)

        return state_group  # type: ignore
