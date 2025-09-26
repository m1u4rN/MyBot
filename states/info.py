from telebot.handler_backends import State, StatesGroup

class UserInfoState(StatesGroup):
    name = State()
    age = State()