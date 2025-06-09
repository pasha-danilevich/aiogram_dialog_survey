from enum import StrEnum
from typing import Callable, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from aiogram_dialog_survey.entities.button import Button

T = TypeVar('T')
TypeFactory = Callable[[str], T]


class QuestionType(StrEnum):
    TEXT_INPUT = "TextInput"
    SELECT = "Select"
    MULTISELECT = "Multiselect"


class Question(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    question_type: QuestionType
    text: str
    is_required: bool
    buttons: Optional[List[Button]] = None
    validator: Optional[TypeFactory] = None

    @model_validator(mode='after')
    def validate_buttons_based_on_type(self) -> 'Question':
        if self.question_type == QuestionType.TEXT_INPUT:
            if self.buttons:
                raise ValueError("Для TEXT-вопроса кнопки не допускаются")
        elif self.question_type in (QuestionType.SELECT, QuestionType.MULTISELECT):
            if not self.buttons or len(self.buttons) == 0:
                raise ValueError(
                    f"Для {self.question_type.value.upper()}-вопроса обязательны кнопки"
                )
            if len(self.buttons) < 2:
                raise ValueError(
                    f"Для {self.question_type.value.upper()}-вопроса нужно минимум 2"
                    " кнопки"
                )
        return self

    @field_validator('buttons')
    def validate_unique_button_callbacks(
        cls, buttons: Optional[List[Button]]
    ) -> Optional[List[Button]]:
        if buttons:
            button_callbacks = [button.callback for button in buttons]
            if len(button_callbacks) != len(set(button_callbacks)):
                raise ValueError("callback кнопок должны быть уникальными")
        return buttons
