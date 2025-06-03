# handler.py
import logging
from abc import ABC
from functools import partial

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Data
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Multiselect, Select

from aiogram_dialog_survey.interface import ActionType, IWindowHandler, QuestionName, ISurvey, Question

logger = logging.getLogger(__name__)


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
        await handler.next_or_done(manager)
    
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
        await handler.next_or_done(manager)
    
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
        await handler.next_or_done(manager)
    
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
        await handler.next_or_done(manager)


class WindowHandler(IWindowHandler, ABC):
    SKIP_CONST = "__skipped__"
    
    def __init__(self, survey: ISurvey, question: Question):
        self.survey = survey
        self.question = question
        self.question_name = question.name
    
    def get_widget_key(self) -> QuestionName:
        return self.question_name
    
    def get_handler(self, action_type: ActionType):
        match action_type:
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
        raise ValueError("Unknown action type")
    
    async def process_handler(
        self,
        manager: DialogManager, question_name: QuestionName, action_type: ActionType
    ) -> None:
        """Обрабатывает пользовательское действие в контексте текущего вопроса диалога.

        Вызывается автоматически при любом взаимодействии пользователя с интерфейсом.
        Позволяет реализовать кастомную логику обработки данных для конкретного вопроса.

        Args:
            manager: Менеджер диалога, содержащий текущий контекст
            question_name: Идентификатор текущего вопроса анкеты
            action_type: Тип выполненного пользователем действия
        """
        logger.info(
            'Обработка действия "%s" для вопроса "%s" | Данные: %s',
            action_type,
            question_name,
            manager.dialog_data.get(question_name, 'нет данных'),
        )
    
    async def process_survey_result(
        self,
        manager: DialogManager, result: Data
    ) -> None:
        """Функция запускается в конце анкетирования, после последнего ответа"""
        logger.info(
            'Анкетирование завершилось. Собранные данные: %s',
            result,
        )
    
    async def next_or_done(self, manager: DialogManager):
        try:
            await manager.next()
        except IndexError:
            result_data = manager.dialog_data
            await self.process_survey_result(manager, result_data)