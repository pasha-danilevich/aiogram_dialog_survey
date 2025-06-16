# widget_factory.py
from typing import Dict, Type

from aiogram_dialog_survey.protocols.widget import WidgetProtocol
from aiogram_dialog_survey.protocols.widget_factory import WidgetFactoryProtocol
from aiogram_dialog_survey.widgets import Multiselect, Select, TextInput


class WidgetFactory(WidgetFactoryProtocol):
    _registry: Dict[str, Type[WidgetProtocol]] = {
        'TextInput': TextInput,
        'Select': Select,
        'Multiselect': Multiselect,
        # 'SkipButton': SkipButton,
    }

    @classmethod
    def register(cls, widget_cls: Type[WidgetProtocol]):
        """Декоратор для регистрации классов виджетов."""
        cls._registry[widget_cls.__name__] = widget_cls

    @classmethod
    def create(cls, name: str) -> WidgetProtocol:
        """Фабричный метод для создания виджетов."""
        print(cls._registry)
        if name not in cls._registry:
            raise ValueError(f'Unknown widget type: {name}')
        return object.__new__(cls._registry[name])
