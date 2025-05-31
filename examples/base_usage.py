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
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from aiogram_dialog_survey import StartSurvey, Survey
from examples import env, survey_static

logging.getLogger('aiogram_dialog_survey').setLevel(logging.DEBUG)
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s')

API_TOKEN = env.TOKEN


class MainSG(StatesGroup):
    default = State()


survey_data = survey_static.survey

survey = Survey(name='survey', questions=survey_data, use_numbering=False)
survey_dialog = survey.to_dialog()

main_menu = Dialog(
    Window(
        Const("Привет. Это бот"),
        Button(Const("Выполни какое-то действие"), id="some_action"),
        StartSurvey(Const("Пройти IT опрос"), survey),
        state=MainSG.default,
    ),
)


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.default)


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(main_menu, survey_dialog)
    dp.message.register(start, CommandStart())

    setup_dialogs(dp)

    await dp.start_polling(Bot(token=API_TOKEN))


if __name__ == "__main__":
    asyncio.run(main())
