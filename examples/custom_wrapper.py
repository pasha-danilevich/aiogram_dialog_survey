import asyncio

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
from aiogram_dialog.widgets.kbd import Button, Start
from aiogram_dialog.widgets.text import Const

from aiogram_dialog_survey import Survey
from aiogram_dialog_survey.window import Wrapper
from examples import env, survey_static

API_TOKEN = env.TOKEN


class MainSG(StatesGroup):
    default = State()


survey = survey_static.survey


class MyCustomWrapper(Wrapper):
    start_message = 'my custom start message'


factory = Survey(name='some', questions=survey, wrapper=MyCustomWrapper)
start_state = factory.get_first_state()
questionnaire_dialog = factory.to_dialog()

main_menu = Dialog(
    Window(
        Const("Привет. Это бот"),
        Button(Const("Выполни какое-то действие"), id="some_action"),
        Start(Const("Пройти опрос"), id="survey", state=start_state),
        state=MainSG.default,
    ),
)


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(MainSG.default)


async def main():
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=storage)
    dp.include_routers(main_menu, questionnaire_dialog)

    dp.message.register(start, CommandStart())
    setup_dialogs(dp)
    print('bot started')
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
