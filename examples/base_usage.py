import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram_dialog import (
    DialogManager,
    setup_dialogs,
)

from aiogram_dialog_survey import Survey
from examples import env, survey_static

logging.getLogger('aiogram_dialog_survey').setLevel(logging.DEBUG)
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s')


survey_data = survey_static.survey
survey = Survey(name='survey', questions=survey_data)
survey_dialog = survey.to_dialog()


async def start_handler(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(survey.state_manager.get_first_state())


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(survey_dialog)
    dp.message.register(start_handler, CommandStart())

    setup_dialogs(dp)

    await dp.start_polling(Bot(token=env.TOKEN))


if __name__ == "__main__":
    asyncio.run(main())
