from aiogram_dialog.widgets.kbd import Button, Back, Cancel
from aiogram_dialog.widgets.text import Const

from aiogram_dialog_survey.protocols.navigation_button import NavigationButtonProtocol


class NavigationButton(NavigationButtonProtocol):
    BACK_BUTTON_TEXT = 'Назад'
    CANCEL_BUTTON_TEXT = 'Отменить заполнение'
    
    def render(self, order: int) -> list[Button]:
        buttons = []
        
        if order == 0:
            pass
        else:
            buttons.append(Back(Const(self.BACK_BUTTON_TEXT)))
        
        buttons.append(Cancel(Const(self.CANCEL_BUTTON_TEXT)))
        
        return buttons