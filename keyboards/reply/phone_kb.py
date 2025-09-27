from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def phone_request_kb(one_time: bool = True) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=one_time)
    kb.add(KeyboardButton("Отправить номер телефона", request_contact=True))
    return kb

def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()

