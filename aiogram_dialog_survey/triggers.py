from typing import Optional

from aiogram_dialog.api.entities import Data, ShowMode, StartMode
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.kbd import Start as AiogramDialogStart
from aiogram_dialog.widgets.kbd.button import OnClick
from aiogram_dialog.widgets.text import Text

from aiogram_dialog_survey.protocols.survey import SurveyProtocol


class StartSurvey(AiogramDialogStart):
    def __init__(
        self,
        text: Text,
        survey: 'SurveyProtocol',
        id: str = "survey",
        data: Data = None,
        on_click: Optional[OnClick] = None,
        show_mode: Optional[ShowMode] = None,
        mode: StartMode = StartMode.NORMAL,
        when: WhenCondition = None,
    ):
        super().__init__(
            text=text,
            id=id,
            state=survey.state_manager.get_first_state(),
            data=data,
            on_click=on_click,
            show_mode=show_mode,
            mode=mode,
            when=when,
        )
