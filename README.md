# Документация по библиотеке aiogram_dialog_survey


## Обзор

Библиотека `aiogram_dialog_survey` предоставляет инструменты для легкого создания больших интерактивных анкет в Telegram ботах на основе `aiogram` и `aiogram_dialog`. Основные возможности:

- Поддержка различных типов вопросов: текстовый ввод, выбор одного варианта, множественный выбор
- Генерация диалоговых окон для каждого вопроса. Ощутимо уменьшает кол-во повторяющегося, рутинного кода
- Кастомизация обработчиков событий. Достаточно написать один обработчик, который будет взаимодействовать с ответами от пользователя

## Быстрый старт

### Установка
```bash
pip install aiogram_dialog_survey
```

### Минимальный пример бота
```python
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import DialogManager, setup_dialogs

from aiogram_dialog_survey import Survey, StartSurvey
from aiogram_dialog_survey.interface import Question, QuestionType, Button

# Определяем вопросы анкеты
questions = [
    Question(
        name="name",
        question_type=QuestionType.TEXT,
        text="Как вас зовут?",
        is_required=True
    ),
    Question(
        name="age",
        question_type=QuestionType.SELECT,
        text="Сколько вам лет?",
        is_required=True,
        buttons=[
            Button(text="До 18", callback="under_18"),
            Button(text="18-25", callback="18_25"),
            Button(text="26-35", callback="26_35"),
            Button(text="Старше 35", callback="over_35"),
        ]
    )
]

# Создаем анкету
survey = Survey(name="user_survey", questions=questions)

async def start_handler(message: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(survey.state_manager.get_first_state())

async def main():
    bot = Bot(token="YOUR_BOT_TOKEN")
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем анкету как диалог
    dp.include_router(survey.to_dialog())
    dp.message.register(start_handler, CommandStart())

    setup_dialogs(dp)
    await dp.start_polling(bot)
```

## Создание анкеты

### Определение вопросов

Вопросы определяются с помощью класса `Question`:

```python
from aiogram_dialog_survey.interface import Question, QuestionType, Button

# Вопросы, их типы и варианты ответов можно хранить в БД или в любом другом удобном месте, чтобы не засорять кодовую базу проекта и сосредоточится на более важных аспектах
questions = [
    Question(
        name="username",  # уникальный идентификатор вопроса
        question_type=QuestionType.TEXT,  # тип вопроса
        text="Введите ваше имя:",  # текст вопроса
        is_required=True  # обязательный ли вопрос
    ),
    Question(
        name="hobbies",
        question_type=QuestionType.MULTISELECT,
        text="Выберите ваши увлечения:",
        is_required=False,
        buttons=[
            Button(text="Спорт", callback="sport"),
            Button(text="Музыка", callback="music"),
            Button(text="Кино", callback="movies"),
        ]
    ),
    #
    # еще очень-очень много вопросов
    #
    Question(
        name="height",
        question_type=QuestionType.TEXT,
        text="Введите ваш рост:",
        is_required=True
    ),
]
```

### Доступные типы вопросов:

1. `QuestionType.TEXT` - текстовый ввод
2. `QuestionType.SELECT` - выбор одного варианта из списка
3. `QuestionType.MULTISELECT` - множественный выбор

### Создание анкеты

```python
from aiogram_dialog_survey import Survey

survey = Survey(
    name="user_survey",  # уникальное имя анкеты
    questions=questions,  # список вопросов
    use_numbering=True  # показывать нумерацию вопросов (по умолчанию True)
)
```

### Подключение анкеты к роутеру

Подключение происходит точно так же, как с обычными `aiogram-dialog` диалогами

```python
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher(storage=MemoryStorage())

# Добавляем анкету как диалог
dp.include_router(survey.to_dialog())
```

## Кастомизация

### Пользовательские обработчики событий

Вы можете создать собственный обработчик событий, унаследовавшись от `IWindowHandler`:

```python
from aiogram_dialog_survey.interface import IWindowHandler, ActionType
from aiogram_dialog import DialogManager

class CustomHandler(IWindowHandler):
    @staticmethod
    async def process_handler(
        manager: DialogManager,
        question_name: str,
        action_type: ActionType
    ) -> None:
	    answer = manager.dialog_data.get(question_name)
        # Кастомная логика обработки событий
        print(f"Пользователь ответил: "{answer}" на вопрос {question_name}")

# Использование кастомного обработчика
survey = Survey(
    name="custom_survey",
    questions=questions,
    handler=CustomHandler
)
```
Такой обработчик отлично подойдет, если вы хотите каждый раз, когда пользователь отвечает на вопрос, обрабатывать его и, допустим, записывать в БД ответ пользователя и его прогресс прохождения анкеты.

В `process_handler` вы так же можете запускать еще `subdialog` в зависимости от ответа
```python
from aiogram_dialog_survey.interface import IWindowHandler, ActionType
from aiogram_dialog import DialogManager

from your_module import music_artist_survey

class CustomHandler(IWindowHandler):
    @staticmethod
    async def process_handler(
        manager: DialogManager,
        question_name: str,
        action_type: ActionType
    ) -> None:
	    answer = manager.dialog_data.get(question_name)
        if question_name == 'do_you_like_music' and answer == 'yes':
	        manager.start(music_artist_survey.state_manager.get_first_state())


```
### Обработка результатов анкеты

Для обработки результатов анкеты можно использовать callback-функцию `on_process_result`:

```python
async def survey_result_handler(result, dialog_manager: DialogManager):
    print("Результаты анкеты:", result)
    await dialog_manager.event.answer("Спасибо за заполнение анкеты!")

survey_dialog = survey.to_dialog(on_process_result=survey_result_handler)
```

## Расширенные возможности

### Интеграция с существующими диалогами

Вы можете добавить анкету как часть большего диалога, в данном примере, `StartSurvey` напустить `subdialog` с анкетой, по завершению которой вы можете получить результат в вашем обработчике `on_result`:

```python
from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const
from aiogram_dialog_survey import StartSurvey

class MainSG(StatesGroup):
    start = State()
    survey = State()
    finish = State()

main_dialog = Dialog(
    Window(
        Const("Добро пожаловать!"),
        StartSurvey(
            Const("Начать анкету"),
            survey,
            id="start_survey"
        ),
        state=MainSG.start,
    ),
    Window(
        Const("Спасибо за участие!"),
        state=MainSG.finish,
    )
)

async def survey_result_handler(result, dialog_manager: DialogManager):
    print("Результаты анкеты:", result)
    await dialog_manager.switch_to(state=MainSG.finish)

survey_dialog = survey.to_dialog(on_process_result=survey_result_handler)
# Добавляем оба диалога в диспетчер
dp.include_routers(main_dialog, survey_dialog)
```
## Примеры использования

### Полный пример бота с анкетой

```python
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import DialogManager, setup_dialogs

from aiogram_dialog_survey import Survey
from aiogram_dialog_survey.interface import Question, QuestionType, Button

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Определение вопросов анкеты
questions = [
    Question(
        name="name",
        question_type=QuestionType.TEXT,
        text="Как вас зовут?",
        is_required=True
    ),
    Question(
        name="age_group",
        question_type=QuestionType.SELECT,
        text="Ваша возрастная группа?",
        is_required=True,
        buttons=[
            Button(text="До 18", callback="under_18"),
            Button(text="18-25", callback="18_25"),
            Button(text="26-35", callback="26_35"),
            Button(text="36-45", callback="36_45"),
            Button(text="Старше 45", callback="over_45"),
        ]
    ),
    Question(
        name="interests",
        question_type=QuestionType.MULTISELECT,
        text="Какие темы вам интересны? (можно выбрать несколько)",
        is_required=False,
        buttons=[
            Button(text="Технологии", callback="tech"),
            Button(text="Наука", callback="science"),
            Button(text="Искусство", callback="art"),
            Button(text="Спорт", callback="sport"),
        ]
    )
]

# Создание анкеты
survey = Survey(
    name="user_profile",
    questions=questions,
    use_numbering=True
)

async def start_handler(message: types.Message, dialog_manager: DialogManager):
	# метод get_first_state() можно использовать, если вы хотите запустить анкету не с помощью кнопки StartSurvey, как мы это делаем в существующем диалоге, а благодаря dialog_manager
    await dialog_manager.start(survey.state_manager.get_first_state())

async def survey_result_handler(result, dialog_manager: DialogManager):
    await dialog_manager.event.answer(
        "Спасибо за заполнение анкеты! Ваши ответы сохранены."
    )
    logging.info("Сохраняем результаты анкеты: %s", result)

async def main():
    bot = Bot(token="YOUR_BOT_TOKEN")
    dp = Dispatcher(storage=MemoryStorage())

    # Добавляем анкету с обработчиком результатов
    dp.include_router(survey.to_dialog(on_process_result=survey_result_handler))
    dp.message.register(start_handler, CommandStart())

    setup_dialogs(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```
