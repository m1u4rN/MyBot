import os
import re
from telebot.types import Message, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from loader import bot
from keyboards.reply import phone_kb
from database.db import (
    get_client_by_user_id,
    get_client_by_phone,
    create_client,
    update_client_user_id_for_phone,
    format_amount,
)

@bot.message_handler(content_types=["contact"])
def handle_contact(message: Message):
    c = message.contact

    if c.user_id and (c.user_id != message.from_user.id):
        bot.reply_to(message, "Пожалуйста, отправьте свой номер через кнопку ниже.")
        return

    user_id = message.from_user.id
    phone = c.phone_number
    name = c.first_name or message.from_user.first_name

    client = get_client_by_user_id(user_id)
    existed = False

    if not client:
        client = get_client_by_phone(phone)

        if client:
            if not client.get("user_id"):
                update_client_user_id_for_phone(phone, user_id)
                client["user_id"] = user_id
            existed = True
        else:
            create_client(
                user_id=user_id,
                phone=phone,
                name=name,
            )
            client = get_client_by_user_id(user_id)
            existed = False
    else:
        existed = True

    bal = format_amount(client["bonus_balance"])
    if existed:
        bot.send_message(
            message.chat.id,
            f"Вы уже являетесь участником нашей программы лояльности.\nБонусный баланс: {bal}",
            reply_markup=phone_kb.remove_kb()
        )
    else:
        bot.send_message(
            message.chat.id,
            f"Спасибо, {name}! Номер {phone} получил. Вы зарегистрированы.\nТекущий баланс: {bal}",
            reply_markup=phone_kb.remove_kb()
        )

    webapp_url = os.getenv("WEBAPP_URL") or os.getenv("MINIAPP_URL")
    if webapp_url:
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(
            "Заполнить анкету (мини-приложение)",
            web_app=WebAppInfo(url=webapp_url)
        ))
        bot.send_message(
            message.chat.id,
            "Для завершения регистрации откройте мини-приложение:",
            reply_markup=kb
        )
    else:
        bot.send_message(
            message.chat.id,
            "Скоро появится мини-приложение с анкетой — пришлю кнопку здесь."
        )

PHONE_RE = re.compile(r'^\+?\d[\d\-\s\(\)]{7,}$')
@bot.message_handler(func=lambda m: bool(m.text) and bool(PHONE_RE.match(m.text)))
def handle_phone_text(message: Message):
    bot.reply_to(
        message,
        "Лучше отправить номер через кнопку «Отправить номер телефона» — так Telegram подтверждает, что это ваш номер."
    )
