from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from loader import bot
from keyboards.reply import phone_kb


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



    bot.send_message(message.chat.id, CAPTION, parse_mode="HTML")


    bot.send_message(message.chat.id, HINT, reply_markup=phone_kb.phone_request_kb(), parse_mode="HTML")
