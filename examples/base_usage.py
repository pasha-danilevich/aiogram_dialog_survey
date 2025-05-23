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

from aiogram_dialog_survey.factory.dialog import QuestionnaireFactory
from aiogram_dialog_survey.interface import QuestionDict, QuestionType, ButtonDict

API_TOKEN = "7886751328:AAGMynt9zQhWqrgbe0gaNq3d-MaYZZ8IexQ"


class MainSG(StatesGroup):
    default = State()


# Опросник из 4 вопросов на тему IT
survey: list[QuestionDict] = [
    {
        "name": "favorite_language",
        "question_type": QuestionType.SELECT,
        "text": "Какой ваш любимый язык программирования?",
        "is_required": True,
        "options": [
            {"text": "Python", "id": "python"},
            {"text": "JavaScript", "id": "js"},
            {"text": "Java", "id": "java"},
            {"text": "C++", "id": "cpp"},
        ],
    },
    {
        "name": "years_experience",
        "question_type": QuestionType.TEXT,
        "text": "Сколько лет вы занимаетесь программированием?",
        "is_required": True,
        "options": None,
    },
    {
        "name": "preferred_tools",
        "question_type": QuestionType.MULTISELECT,
        "text": "Какие инструменты разработки вы используете?",
        "is_required": False,
        "options": [
            {"text": "Git", "id": "git"},
            {"text": "Docker", "id": "docker"},
            {"text": "VS Code", "id": "vscode"},
            {"text": "PyCharm", "id": "pycharm"},
            {"text": "Jira", "id": "jira"},
        ],
    },
    {
        "name": "interested_topics",
        "question_type": QuestionType.MULTISELECT,
        "text": "Какие темы в IT вам наиболее интересны?",
        "is_required": True,
        "options": [
            {"text": "Искусственный интеллект", "id": "ai"},
            {"text": "Веб-разработка", "id": "web"},
            {"text": "Мобильная разработка", "id": "mobile"},
            {"text": "Кибербезопасность", "id": "security"},
            {"text": "Облачные технологии", "id": "cloud"},
        ],
    },
]

factory = QuestionnaireFactory(survey_name='some', questions=survey)
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
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
