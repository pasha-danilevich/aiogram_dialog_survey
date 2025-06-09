from abc import abstractmethod
from typing import Self, Tuple, Union

from aiogram import F
from aiogram.types import Message
from aiogram_dialog.widgets.input import TextInput as AiogramTextInput
from aiogram_dialog.widgets.kbd import Button as AiogramDialogButton
from aiogram_dialog.widgets.kbd import Column
from aiogram_dialog.widgets.kbd import Multiselect as AiogramDialogMultiselect
from aiogram_dialog.widgets.kbd import Select as AiogramDialogSelect
from aiogram_dialog.widgets.text import Const, Format

from aiogram_dialog_survey.entities.action_type import ActionType
from aiogram_dialog_survey.entities.question import Question
from aiogram_dialog_survey.protocols.handler import HandlerProtocol


class WidgetFactory:
    class Unknown(Exception):
        pass

    @classmethod
    def _get_all_subclasses(cls):
        for subclass in cls.__subclasses__():
            yield subclass
            for recursive_subclass in subclass._get_all_subclasses():
                yield recursive_subclass

    def __new__(cls, name: str) -> Self:
        for subclass in cls._get_all_subclasses():
            if subclass.name == name:
                # Using "object" base class method avoids recursion here.
                return object.__new__(subclass)
        else:  # no subclass with matching name found (and no default defined)
            raise WidgetFactory.Unknown(
                'name "{}" has no known WidgetFactory type'.format(name)
            )

    @abstractmethod
    def render(self, question: Question, handler: HandlerProtocol):
        raise NotImplementedError


class TextInput(WidgetFactory):
    name = 'TextInput'

    def render(self, question: Question, handler: HandlerProtocol):
        return AiogramTextInput(
            id=f'input_{question.name.strip()}',
            on_success=handler.get_handler(ActionType.ON_INPUT_SUCCESS),
            type_factory=question.validator,
            on_error=self._on_error,
        )

    @staticmethod
    async def _on_error(message: Message, _, __, error: ValueError):
        await message.answer(str(error))


class Select(WidgetFactory):
    name = 'Select'
    WidgetButton = Tuple[str, Union[str, int]]

    def render(self, question: Question, handler: HandlerProtocol):
        return Column(
            AiogramDialogSelect(
                text=Format("{item[0]}"),
                id=f'select_{question.name.strip()}',
                item_id_getter=self._item_id_getter,
                items=self._create_buttons(question),
                on_click=handler.get_handler(
                    ActionType.ON_SELECT
                ),  # используем partial
            )
        )

    @property
    def _item_id_getter(self):
        return lambda x: x[1]

    @staticmethod
    def _create_buttons(question: Question) -> list[WidgetButton]:
        return [(button.text, button.callback) for button in question.buttons]


class Multiselect(Select):
    name = "Multiselect"
    ACCEPT_BUTTON_TEXT = "Подтвердить выбор"

    def render(self, question: Question, handler: HandlerProtocol):
        return Column(
            AiogramDialogMultiselect(
                Format("✓ {item[0]}"),  # Selected item format
                Format("{item[0]}"),  # Unselected item format
                id=f'multi_{question.name.strip()}',
                item_id_getter=self._item_id_getter,
                items=self._create_buttons(question),
                on_click=handler.get_handler(ActionType.ON_MULTISELECT),
            ),
            AiogramDialogButton(
                Const(self.ACCEPT_BUTTON_TEXT),
                id='__accept__',
                on_click=handler.get_handler(ActionType.ON_ACCEPT),
                when=F["dialog_data"][handler.get_widget_key()].len()
                > 0,  # Only show when items are selected
            ),
        )


class SkipButton(WidgetFactory):
    name = 'SkipButton'
    BUTTON_TEXT = "Пропустить вопрос"

    def render(self, question: Question, handler: HandlerProtocol):
        return AiogramDialogButton(
            Const(self.BUTTON_TEXT),
            id=f'skip_{question.name.strip()}',
            on_click=handler.get_handler(ActionType.ON_SKIP),
        )


if __name__ == '__main__':
    from aiogram_dialog_survey.handler import FakeHandler
    from examples.survey_static import survey

    # Usage
    for q in survey:
        handler_ = FakeHandler()
        widget = WidgetFactory(q.question_type).render(q, handler_)
        print(widget)
