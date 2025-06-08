from abc import abstractmethod
from typing import Callable, Protocol, TypeVar

from aiogram.types import Message

T = TypeVar('T')
TypeFactory = Callable[[str], T]


class ValidatorProtocol(Protocol):
    @property
    @abstractmethod
    def type_factory(self) -> TypeFactory:
        pass

    @staticmethod
    @abstractmethod
    async def on_error(message: Message, _, __, error: ValueError):
        pass
