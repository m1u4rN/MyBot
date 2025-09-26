from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from loader import bot


START_PHOTO_PATH = ""

CAPTION = (
    "Отправь номер телефона, чтобы я зарегистрировал тебя "
    "в программе лояльности или помог проверить накопленный баланс баллов!"
)

HINT = (
    "Чтобы стать участником программы лояльности, нажмите кнопку "
    "<b>Отправить номер телефона</b> ниже"
)

@bot.message_handler(commands=["start"])
def bot_start(message: Message):

    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("Отправить номер телефона", request_contact=True))

    bot.send_message(message.chat.id, CAPTION, parse_mode="HTML")


    bot.send_message(message.chat.id, HINT, reply_markup=kb, parse_mode="HTML")
