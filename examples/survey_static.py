from typing import List

from aiogram_dialog_survey.entities.button import Button
from aiogram_dialog_survey.entities.question import Question, WidgetType


def validate_int(text: str) -> int:
    try:
        text = int(text)
    except ValueError:
        # В ValueError можно передать текст сообщения, который появится у пользователя
        raise ValueError('Нужно написать цифрой. Например: 3')
    return text


# Опросник из 4 вопросов на тему IT
survey: List[Question] = [
    Question(
        name="favorite_language",
        widget_type=WidgetType.SELECT,
        text="Какой ваш любимый язык программирования?",
        is_required=True,
        buttons=[
            Button(text="Python", callback="python"),
            Button(text="JavaScript", callback="js"),
            Button(text="Java", callback="java"),
            Button(text="C++", callback="cpp"),
        ],
    ),
    Question(
        name="years_experience",
        widget_type=WidgetType.TEXT_INPUT,
        text="Сколько лет вы занимаетесь программированием?",
        is_required=True,
        validator=validate_int,
    ),
    Question(
        name="preferred_tools",
        widget_type=WidgetType.MULTISELECT,
        text="Какие инструменты разработки вы используете?",
        is_required=False,
        buttons=[
            Button(text="Git", callback="git"),
            Button(text="Docker", callback="docker"),
            Button(text="VS Code", callback="vscode"),
            Button(text="PyCharm", callback="pycharm"),
            Button(text="Jira", callback="jira"),
        ],
    ),
    Question(
        name="interested_topics",
        widget_type=WidgetType.MULTISELECT,
        text="Какие темы в IT вам наиболее интересны?",
        is_required=True,
        buttons=[
            Button(text="Искусственный интеллект", callback="ai"),
            Button(text="Веб-разработка", callback="web"),
            Button(text="Мобильная разработка", callback="mobile"),
            Button(text="Кибербезопасность", callback="security"),
            Button(text="Облачные технологии", callback="cloud"),
        ],
    ),
]
