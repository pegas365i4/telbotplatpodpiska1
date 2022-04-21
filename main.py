import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
import markups as nav # Сократил название, чтобы было удобнее
from db import Database

import time
import datetime


TOKEN = "5******3:A***************************4" # input my token
YOOTOKEN = "3********8:TEST:3*****8" # input token Юкассы [Если выбран бот ЮKassa: тест]
# Как получить своего бота к боту ЮKassa
# (https://yookassa.ru/docs/support/payments/onboarding/integration/cms-module/telegram)

logging.basicConfig(level=logging.INFO)

# Initialize bot
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

db = Database('database.db')

# Метод Переводим дни в секунды:
def days_to_seconds(days):
    return days * 24 * 60 * 60
# Метод Высчитываем сколько времени будет активна подписка:
def time_sub_day(get_time):
    time_now = int(time.time())
    middle_time = int(get_time) - time_now

    if middle_time <=0:
        return False
    else:
        dt = str(datetime.timedelta(seconds=middle_time))
        dt = dt.replace("days", "дней") # Заменяем англ. слова на русские
        dt = dt.replace("day", "день")
        return dt

# Приветствие:
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if(not db.user_exists(message.from_user.id)): # Если наш пользователь еще не зарегистрирован, то выполняем регистрацию
        # Создаём нового пользователя:
        db.add_user(message.from_user.id)
        await bot.send_message(message.from_user.id, "Укажите ваш ник")
    else: # Если уже зарегистрирован, то пишем сообщение и открываем ему меню!
        await bot.send_message(message.from_user.id, "Вы уже зарегистрированы!", reply_markup=nav.mainMenu)

@dp.message_handler()
async def bot_message(message: types.Message):
    if message.chat.type == 'private':  # Проверяем что мы в приватном режиме. РАБОТАЕТ ТОЛЬКО В ПРИВАТНОМ РЕЖИМЕ!
        if message.text == '👤 ПРОФИЛЬ':
            user_nickname = "Ваш ник: " + db.get_nickname(message.from_user.id)
            user_sub = time_sub_day(db.get_time_sub(message.from_user.id))
            if user_sub == False:
                user_sub = "Нет"
            user_sub = "\nПодписка: " + user_sub
            await bot.send_message(message.from_user.id, user_nickname + user_sub)

        elif message.text == '❤ ПОДПИСКА':
            await bot.send_message(message.from_user.id, "Описание подписки", reply_markup=nav.sub_inline_markup)

        elif message.text == '🍸 ТОЛЬКО ДЛЯ ОПЛАТИВШИХ':
            if db.get_sub_status(message.from_user.id):
                await bot.send_message(message.from_user.id, "Секретный список пользователей!!!")
            else:
                await bot.send_message(message.from_user.id, "Купите подписку, чтобы воспользоваться данной функцией!")

        else:
            if db.get_signup(message.from_user.id) == "setnickname":
                if(len(message.text) > 15):
                    await bot.send_message(message.from_user.id, "Никнейм не должен превышать 15 символов")
                elif '@' in message.text or '/' in message.text:
                    await bot.send_message(message.from_user.id, "Вы ввели запрещенный символ")
                else:
                    db.set_nickname(message.from_user.id, message.text)
                    db.set_signup(message.from_user.id, "done")
                    await bot.send_message(message.from_user.id, "Регистрация прошла успешно!", reply_markup=nav.mainMenu)
            else:
                await bot.send_message(message.from_user.id, "Не понятно что Вы ввели...")

# Создаём декоратор
@dp.callback_query_handler(text="submonth")
async def submonth(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id) # Удалил предыдущее сообщение
    await bot.send_invoice(chat_id=call.from_user.id, title="Оформление подписки", description="Тестовое описание товара", payload="month_sub", provider_token=YOOTOKEN, currency="RUB", start_parameter="test_bot", prices=[{"label": "Руб", "amount": 15000}])

# Подтверждаем, что у нас есть нужный товар в наличии:
@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Подхватываем, что наш товар уже оплачен и выдаем сообщение об удачной покупке:
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_pay(message: types.Message):
    if message.successful_payment.invoice_payload == "month_sub":
        # Подписываем пользователя
        time_sub = int(time.time()) + days_to_seconds(30)
        db.set_time_sub(message.from_user.id, time_sub)
        await bot.send_message(message.from_user.id, "Вам выдана подписка на месяц!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)