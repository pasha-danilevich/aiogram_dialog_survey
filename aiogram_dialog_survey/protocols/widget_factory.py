from typing import Protocol, Type

from aiogram_dialog_survey.protocols.widget import WidgetProtocol


class WidgetFactoryProtocol(Protocol):
    @classmethod
    def register(cls, widget_cls: Type[WidgetProtocol]):
        """Декоратор для регистрации классов виджетов."""

    @classmethod
    def create(cls, name: str) -> WidgetProtocol:
        """Фабричный метод для создания виджетов."""
