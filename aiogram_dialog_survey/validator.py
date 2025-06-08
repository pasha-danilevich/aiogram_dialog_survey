from aiogram.types import Message

from aiogram_dialog_survey.protocols.validator import TypeFactory, ValidatorProtocol


class StringValidator(ValidatorProtocol):
    def __init__(self, type_factory: TypeFactory = str):
        super().__init__(type_factory)

    @staticmethod
    async def on_error(message: Message, _, __, error: ValueError):
        pass


class Validator(ValidatorProtocol):
    @staticmethod
    async def on_error(message: Message, _, __, error: ValueError):
        await message.answer(str(error))
