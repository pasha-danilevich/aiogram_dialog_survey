from abc import ABC, abstractmethod
from typing import Union, Tuple

from aiogram import F
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button as AiogramDialogButton
from aiogram_dialog.widgets.kbd import Column
from aiogram_dialog.widgets.kbd import Multiselect as AiogramDialogMultiselect
from aiogram_dialog.widgets.kbd import Select as AiogramDialogSelect
from aiogram_dialog.widgets.text import Format, Const

from aiogram_dialog_survey.interface import QuestionDict, IWindowHandler, ActionType, Button

WidgetButton = Tuple[str, Union[str, int]]

class Widget(ABC):
	@abstractmethod
	def __init__(self, question: QuestionDict, handler: IWindowHandler):
		pass
	
	@abstractmethod
	def create(self):
		pass


class BaseWidget(Widget):
	def __init__(self, question: QuestionDict, handler: IWindowHandler):
		self.question = question
		self.handler = handler
	
	def create(self):
		raise NotImplementedError
	
	@property
	def item_id_getter(self):
		return lambda x: x[1]
	
	def create_items(self) -> list[WidgetButton]:
		return [(x['text'], x['id']) for x in self.question["options"]]


class Text(BaseWidget):
	def create(self):
		return TextInput(
			id=f'input_{self.question["name"]}',
			on_success=self.handler.get_handler(ActionType.ON_INPUT_SUCCESS),
			type_factory=str,
		)


class Select(BaseWidget):
	def create(self):
		return Column(
			AiogramDialogSelect(
				text=Format("{item[0]}"),
				id=f'select_{self.question["name"]}',
				item_id_getter=self.item_id_getter,
				items=self.create_items(),
				on_click=self.handler.get_handler(
					ActionType.ON_SELECT
				),  # используем partial
			)
		)


class Multiselect(BaseWidget):
	ACCEPT_BUTTON_TEXT = "Подтвердить выбор"
	
	def create(self):
		return Column(
			AiogramDialogMultiselect(
				Format("✓ {item[0]}"),  # Selected item format
				Format("{item[0]}"),  # Unselected item format
				id=f'multi_{self.question["name"]}',
				item_id_getter=self.item_id_getter,
				items=self.create_items(),
				on_click=self.handler.get_handler(ActionType.ON_MULTISELECT),
			),
			AiogramDialogButton(
				Const(self.ACCEPT_BUTTON_TEXT),
				id='__accept__',
				on_click=self.handler.get_handler(ActionType.ON_ACCEPT),
				when=F["dialog_data"][self.handler.get_widget_key()].len()
				     > 0,  # Only show when items are selected
			),
		)
