from aiogram_dialog_survey.interface import QuestionDict, QuestionType

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
