# widgets.py
from typing import Tuple, Union

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
from aiogram_dialog_survey.protocols.widget import WidgetProtocol


class TextInput(WidgetProtocol):
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


class Select(WidgetProtocol):
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


class SkipButton(WidgetProtocol):
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
        # widget = WidgetFactory.create(q.widget_type)
        # result = widget.render(q, FakeHandler())
        # print(result)
