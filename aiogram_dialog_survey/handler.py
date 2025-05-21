from abc import ABC
from functools import partial

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Multiselect, Select

from aiogram_dialog_survey.interface import ActionType, IWindowHandler, QuestionName, ProcessHandler


class Handlers:
    @staticmethod
    async def select(
        callback: CallbackQuery,
        widget: Select,
        manager: DialogManager,
        item_id: str,
        handler: 'WindowHandler',
    ):
        key = handler.get_widget_key()
        manager.dialog_data[key] = item_id
        

        await handler.process_handler(manager, key, ActionType.ON_SELECT)
        await handler.end_handler(manager)

    @staticmethod
    async def skip(
        callback: CallbackQuery,
        button: Button,
        manager: DialogManager,
        handler: 'WindowHandler',
    ):
        key = handler.get_widget_key()
        manager.dialog_data[key] = handler.SKIP_CONST
        

        await handler.process_handler(manager, key, ActionType.ON_SKIP)
        await handler.end_handler(manager)

    @staticmethod
    async def input(
        message: Message,
        widget: ManagedTextInput,
        manager: DialogManager,
        text: str,
        handler: 'WindowHandler',
    ):
        key = handler.get_widget_key()
        manager.dialog_data[key] = text

        await handler.process_handler(manager, key, ActionType.ON_INPUT_SUCCESS)
        await handler.end_handler(manager)

    @staticmethod
    async def multiselect(
        callback: CallbackQuery,
        widget: Multiselect,
        manager: DialogManager,
        item_id: int,
        handler: 'WindowHandler',
    ) -> None:
        """Обработка множественного выбора"""
        key = handler.get_widget_key()
        selected = manager.dialog_data.setdefault(key, [])

        if item_id in selected:
            selected.remove(item_id)
        else:
            selected.append(item_id)

        manager.dialog_data[key] = selected
        await handler.process_handler(manager, key, ActionType.ON_MULTISELECT)


    @staticmethod
    async def on_accept(
        callback: CallbackQuery,
        widget: Button,
        manager: DialogManager,
        handler: 'WindowHandler',
    ):
        key = handler.get_widget_key()
        
        await handler.process_handler(manager, key, ActionType.ON_ACCEPT)
        await handler.end_handler(manager)


class WindowHandler(IWindowHandler, ABC):
    SKIP_CONST = "__skipped__"

    def __init__(self, question_name: str):
        self.question_name = question_name

    def get_widget_key(self) -> QuestionName:
        return self.question_name

    def get_handler(self, handler_type: ActionType):
        match handler_type:
            case ActionType.ON_SELECT:
                return partial(Handlers.select, handler=self)
            case ActionType.ON_INPUT_SUCCESS:
                return partial(Handlers.input, handler=self)
            case ActionType.ON_SKIP:
                return partial(Handlers.skip, handler=self)
            case ActionType.ON_MULTISELECT:
                return partial(Handlers.multiselect, handler=self)
            case ActionType.ON_ACCEPT:
                return partial(Handlers.on_accept, handler=self)

    @staticmethod
    async def process_handler(
        manager: DialogManager, widget_key: QuestionName, action_type: ActionType
    ) -> None:
        """Запускается при каждом действии (HandlerActionType) в каждом окне (вопросе) диалога (анкеты).
        Переопределите данный метод для внедрения собственной логики взаимодействия с данными
        """
        pass

    @staticmethod
    async def end_handler(manager: DialogManager):
        try:
            await manager.next()
        except IndexError:
            print('end')
            await manager.done(
                result={"dialog_data": manager.dialog_data}
            )  # TODO: пока не ясно, с каким ключом надо возвращать дату
