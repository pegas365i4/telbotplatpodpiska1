from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


# --- Main Menu ---
btnProfile = KeyboardButton('👤 ПРОФИЛЬ')
btnSub = KeyboardButton('❤ ПОДПИСКА')
btnList = KeyboardButton('🍸 ТОЛЬКО ДЛЯ ОПЛАТИВШИХ')

mainMenu = ReplyKeyboardMarkup(resize_keyboard=True)
mainMenu.add(btnProfile, btnSub, btnList)

# --- Subscribe Inline Buttons ---
sub_inline_markup = InlineKeyboardMarkup(row_width=1)

btnSubMonth = InlineKeyboardButton(text="Месяц - 150 рублей", callback_data="submonth")

sub_inline_markup.insert(btnSubMonth)

