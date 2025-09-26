import re
from telebot.types import Message, ReplyKeyboardRemove
from loader import bot


@bot.message_handler(content_types=["contact"])
def handle_contact(message: Message):
    c = message.contact

    if c.user_id and (c.user_id != message.from_user.id):
        bot.reply_to(message, "Пожалуйста, отправьте свой номер через кнопку ниже.")
        return

    phone = c.phone_number
    name = c.first_name or message.from_user.first_name

    # TODO: здесь можно сохранить phone в БД/CSV
    bot.send_message(
        message.chat.id,
        f"Спасибо, {name}! Номер {phone} получил. Для завершения регистрации, заполните небольшую анкету: ",
        reply_markup=ReplyKeyboardRemove()
    )

PHONE_RE = re.compile(r'^\+?\d[\d\-\s\(\)]{7,}$')
@bot.message_handler(func=lambda m: bool(m.text) and bool(PHONE_RE.match(m.text)))
def handle_phone_text(message: Message):
    digits = re.sub(r"\D", "", message.text)
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    phone = "+" + digits if not digits.startswith("+") else "+" + digits
    bot.reply_to(message, f"Принял номер {phone}. В следующий раз удобнее по кнопке ☺️. Для завершения регистрации, заполните небольшую анкету: ")
