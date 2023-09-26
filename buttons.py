from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

markup = ReplyKeyboardMarkup(resize_keyboard=True)
bn1 = KeyboardButton('Сгенерировать пароль 🎲')
pas = markup.add(bn1)

newMarkup = InlineKeyboardMarkup()
bn2 = InlineKeyboardButton('4', callback_data='four')
bn3 = InlineKeyboardButton('6', callback_data='six')
bn4 = InlineKeyboardButton('8', callback_data='eight')
bn5 = InlineKeyboardButton('10', callback_data='ten')
bn6 = InlineKeyboardButton('12', callback_data='twelve')
bn7 = InlineKeyboardButton('14', callback_data='fourteen')
bn8 = InlineKeyboardButton('16', callback_data='sixteen')
bn9 = InlineKeyboardButton('18', callback_data='eighteen')
bnq1 = InlineKeyboardButton('20', callback_data='twenty')
newPas = newMarkup.add(bn2, bn3, bn4, bn5, bn6, bn7, bn8, bn9, bnq1)


mankind = InlineKeyboardMarkup(row_width=1)
mk1 = InlineKeyboardButton('Создать профиль 👤', callback_data='createProfile')
mk2 = InlineKeyboardButton('Все пользователи 🔎', callback_data='allProfile')
mk3 = InlineKeyboardButton('Создать вопрос ✏️', callback_data='createAnswer')
# mk3 = InlineKeyboardButton('Создать пароль 🔒', callback_data='createPassword')
mk4 = InlineKeyboardButton('Пройти викторину✍️', callback_data='quiz')
mk5 = InlineKeyboardButton('Создатель данного бота 👨‍💻', callback_data='admin', url='https://t.me/NouSlide')
menu = mankind.add(mk5).row(mk1, mk2).row(mk3, mk4)


btn_ikb = InlineKeyboardMarkup(row_width=1)
mk1 = InlineKeyboardButton('1', callback_data='gr1')
mk2 = InlineKeyboardButton('2', callback_data='gr2')
mk3 = InlineKeyboardButton('3', callback_data='gr3')
mk4 = InlineKeyboardButton('4', callback_data='gr4')
choice_btn = btn_ikb.add(mk1, mk2, mk3, mk4)


cr_bt = InlineKeyboardMarkup()
button = InlineKeyboardButton('Выбрать', callback_data='choose')
choose_answer = cr_bt.add(button)
