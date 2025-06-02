# examples/base_usage.py
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram_dialog import (
    Dialog,
    DialogManager,
    Window,
    setup_dialogs,
)
from aiogram_dialog.widgets.kbd import Next, SwitchTo
from aiogram_dialog.widgets.text import Const

from aiogram_dialog_survey import StartSurvey, Survey
from examples import survey_static

logging.getLogger('aiogram_dialog_survey').setLevel(logging.DEBUG)
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s')


survey_data = survey_static.survey
survey = Survey(name='survey', questions=survey_data)
survey_dialog = survey.to_dialog()


class MainSG(StatesGroup):
    start = State()
    middle = State()
    end = State()


main_menu = Dialog(
    Window(
        Const("Привет. Это бот"),
        Next(Const("Привет"), id="hello"),
        state=MainSG.start,
    ),
    Window(
        Const("Было бы здорово, если бы ты рассказал про себя немного больше"),
        Next(Const("Не хочу"), id="no"),
        StartSurvey(
            Const("Рассказать"), survey
        ),  # TODO: сделать более наглядный пример с обработчиком результата
        state=MainSG.middle,
    ),
    Window(
        Const("Очень жаль("),
        SwitchTo(Const("Заново"), id='again', state=MainSG.start),
        state=MainSG.end,
    ),
)


async def start_handler(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.start)


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(main_menu, survey_dialog)
    dp.message.register(start_handler, CommandStart())

    setup_dialogs(dp)

    await dp.start_polling(Bot(token='token'))


if __name__ == "__main__":
    asyncio.run(main())
