from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
import sqlite3 as sq
import re
import buttons as but

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from database import create_profile, edit_profile
import database


async def on_startup(_):
    await database.db_start()


bot = Bot('6343794582:AAEIwCa_GD7KxO8W4KkmdFIkJqgpxPH-fUM')
dp = Dispatcher(bot, storage=MemoryStorage())


db = sq.connect('profile.db')
cur = db.cursor()


class ProfileStatesGroup(StatesGroup):

    photo = State()
    name = State()


class QuizzesStatesGroup(StatesGroup):

    main_question = State()
    first_answer = State()
    second_answer = State()
    third_answer = State()
    fourth_answer = State()
    correct_option = State()
    choose_answer = State()


def choice_is_true_answer() -> ReplyKeyboardMarkup:
    cita = ReplyKeyboardMarkup(resize_keyboard=True)
    rkm1 = KeyboardButton('1')
    rkm2 = KeyboardButton('2')
    rkm3 = KeyboardButton('3')
    rkm4 = KeyboardButton('4')
    cita.row(rkm1, rkm2)
    cita.row(rkm3, rkm4)

    return cita


def cancel_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/Выйти'))

    return kb


def cancel_create_question() -> ReplyKeyboardMarkup:
    new_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    new_kb.add(KeyboardButton('/Отмена'))

    return new_kb


@dp.message_handler(commands=['Выйти'], state='*')
async def cancel(message: types.Message, state: FSMContext):
    if state is None:
        return

    await state.finish()
    await message.answer('Вы вышли из поля регистрации 🙅‍♂️', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['Отмена'], state='*')
async def cancel_create(message: types.Message, state: FSMContext):
    if state is None:
        return

    cur.execute("SELECT user_id FROM people WHERE user_id=?", (message.from_user.id,))
    profile = cur.fetchall()
    if message.from_user.id in profile:
        del profile[message.from_user.id]
    await state.finish()
    await message.answer('Вы отменили создание вопроса 🙅‍♂️', reply_markup=types.ReplyKeyboardRemove())


async def show_all_users(callback: types.CallbackQuery, numbers: list) -> None:
    for user in numbers:
        await bot.send_photo(chat_id=callback.message.chat.id,
                             photo=user[1],
                             caption=f'Имя: <b>{user[2]}</b>\nID: <b>{user[0]}</b>',
                             parse_mode='HTML')


@dp.message_handler(commands=['start'])
async def start(message: types.Message) -> None:
    main_text = 'Добро пожаловать в Victor Bot💜 Создавай вопросы и проходи викторины вместе с другими пользователями 👐'
    await message.answer(main_text, reply_markup=but.mankind)


answer_mapping = {
    1: 'main_question',
    2: 'first_answer',
    3: 'second_answer',
    4: 'third_answer',
    5: 'fourth_answer'
}


def generate_callback_data(question_id, answer_index):
    return f"answer_{question_id}_{answer_index}"


current_question = 1


async def send_question(user_id, state):
    random_question = await database.get_all_quest('questions')
    if random_question:
        question_text = random_question[answer_mapping[1]]
        options = [
            random_question[answer_mapping[2]],
            random_question[answer_mapping[3]],
            random_question[answer_mapping[4]],
            random_question[answer_mapping[5]]
        ]

        mnk = InlineKeyboardMarkup(row_width=1)
        for answer_index, option_text in enumerate(options):
            callback_data = generate_callback_data(random_question['question_id'], answer_index + 1)
            button = InlineKeyboardButton(option_text, callback_data=callback_data)
            mnk.add(button)

        await bot.send_message(user_id, question_text, reply_markup=mnk)
    else:
        await bot.send_message(user_id, 'Викторина завершена!')


@dp.callback_query_handler(text='quiz')
async def start_quiz(callback_query: types.CallbackQuery):
    # cur.execute("SELECT id FROM active_users WHERE id=?", (callback_query.from_user.id,))
    # user_passed = cur.fetchall()
    # if not user_passed:
    global current_question
    current_question = 1
    await send_question(callback_query.from_user.id, current_question)
    # else:
    #     await bot.send_message(callback_query.from_user.id, 'Второй раз пройти викторину нельзя 🥲')
    await callback_query.message.delete()

count = 0
emoji = ''


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith("answer"))
async def process_answer(callback_query: types.CallbackQuery, state):
    global current_question, count, emoji
    _, question_index, answer_index = callback_query.data.split("_")
    question_index = int(question_index)
    answer_index = int(answer_index)

    correct_answer_index = database.get_correct_answer_index(question_index)

    if answer_index == correct_answer_index:
        count += 1
    else:
        await callback_query.answer('Неправильный ответ!')

    if count == 0:
        emoji = '😭'
    elif count == 1:
        emoji = '😢'
    elif count == 2:
        emoji = '🙁'
    elif count == 3:
        emoji = '😐'
    elif count == 4:
        emoji = '😌'
    else:
        emoji = '😎'

    text = f'Викторина завершена. {count} правильных ответа из 5 {emoji}'

    await callback_query.message.delete()

    current_question += 1
    if current_question <= 5:  # Предполагаю, что у вас 5 вопросов
        await send_question(callback_query.from_user.id, current_question)
    else:
        # await database.create_active(user_id=callback_query.from_user.id)
        count = 0
        await bot.send_message(callback_query.from_user.id, text)


@dp.callback_query_handler(text='allProfile')
async def get_all_users(callback: types.CallbackQuery):
    numbers = await database.get_all_users()

    if not numbers:
        await callback.message.delete()
        await callback.message.answer('Пользователей нет 😶‍🌫️')
        return await callback.answer()

    await callback.message.delete()
    await show_all_users(callback, numbers)
    await callback.answer()


@dp.callback_query_handler(text='createAnswer')
async def add_new_quiz(message: types.Message):
    cur.execute("SELECT user_id FROM people WHERE user_id=?", (message.from_user.id,))
    user = cur.fetchall()
    if user:
        await bot.send_message(message.from_user.id, 'Отлично!👌 Для начала отправь текст вопроса',
                               reply_markup=cancel_create_question())
        await QuizzesStatesGroup.main_question.set()
    else:
        await bot.send_message(message.from_user.id, 'Для того чтобы создавать вопросы нужно создать профиль 🙅‍♂️')


@dp.message_handler(lambda message, pattern = re.compile(r'^[а-яА-Яa-zA-Z 0-9\u0080-\U0010FFFF?!+",.%«»•-]+$'): not pattern.match(message.text), state=QuizzesStatesGroup.main_question)
async def check_quest(message: types.Message):
    await message.answer('Текст вопроса содержит недопустимые символы ❌')


@dp.message_handler(state=QuizzesStatesGroup.main_question)
async def load_main_quest(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as news_data:
        news_data['main_question'] = message.text

    await message.reply('Отправь текст первого варианта ответа')
    await QuizzesStatesGroup.next()


@dp.message_handler(lambda message, pattern = re.compile(r'^[а-яА-Яa-zA-Z 0-9\u0080-\U0010FFFF?!+",.%«»•-]+$'): not pattern.match(message.text), state=QuizzesStatesGroup.first_answer)
async def check_first_answer(message: types.Message):
    await message.answer('Текст варианта ответа содержит недопустимые символы ❌')


@dp.message_handler(state=QuizzesStatesGroup.first_answer)
async def load_first_variant(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as news_data:
        news_data['first_answer'] = message.text

    await message.reply('Отправь текст второго варианта ответа')
    await QuizzesStatesGroup.next()


@dp.message_handler(lambda message, pattern = re.compile(r'^[а-яА-Яa-zA-Z 0-9\u0080-\U0010FFFF?!+",.%«»•-]+$'): not pattern.match(message.text), state=QuizzesStatesGroup.second_answer)
async def check_second_answer(message: types.Message):
    await message.answer('Текст варианта ответа содержит недопустимые символы ❌')


@dp.message_handler(state=QuizzesStatesGroup.second_answer)
async def load_second_variant(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as news_data:
        news_data['second_answer'] = message.text

    await message.reply('Отправь текст третьего варианта ответа')
    await QuizzesStatesGroup.next()


@dp.message_handler(lambda message, pattern = re.compile(r'^[а-яА-Яa-zA-Z 0-9\u0080-\U0010FFFF?!+",.%«»•-]+$'): not pattern.match(message.text), state=QuizzesStatesGroup.third_answer)
async def check_third_answer(message: types.Message):
    await message.answer('Текст варианта ответа содержит недопустимые символы ❌')


@dp.message_handler(state=QuizzesStatesGroup.third_answer)
async def load_third_variant(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as news_data:
        news_data['third_answer'] = message.text

    await message.reply('Теперь отправь текст четвертого варианта ответа')
    await QuizzesStatesGroup.next()


@dp.message_handler(lambda message, pattern = re.compile(r'^[а-яА-Яa-zA-Z 0-9\u0080-\U0010FFFF?!+",.%«»•-]+$'): not pattern.match(message.text), state=QuizzesStatesGroup.fourth_answer)
async def check_fourth_answer(message: types.Message):
    await message.answer('Текст варианта ответа содержит недопустимые символы ❌')


@dp.message_handler(state=QuizzesStatesGroup.fourth_answer)
async def load_fourth_answer(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as news_data:
        news_data['fourth_answer'] = message.text
        rkm = ReplyKeyboardMarkup(resize_keyboard=True)
        rm1 = KeyboardButton(news_data['first_answer'])
        rm2 = KeyboardButton(news_data['second_answer'])
        rm3 = KeyboardButton(news_data['third_answer'])
        rm4 = KeyboardButton(news_data['fourth_answer'])
        rkm.add(rm1, rm2, rm3, rm4)

    await message.reply('Теперь выбери номер правильного ответа', reply_markup=choice_is_true_answer())
    await QuizzesStatesGroup.next()


@dp.message_handler(lambda message, pattern = re.compile(r'^[1-4]$'): not pattern.match(message.text), state=QuizzesStatesGroup.correct_option)
async def check_correct_option(message: types.Message):
    await message.answer('❌ Укажи цифру правильного ответа: 1, 2, 3 или 4')


@dp.message_handler(state=QuizzesStatesGroup.correct_option)
async def process_correct_option(message: types.Message, state: FSMContext):
    async with state.proxy() as news_data:
        news_data['correct_option'] = int(message.text)

    await message.delete()
    await database.create_quiz(state)
    await message.answer('Вопрос успешно создан ✅', reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


@dp.callback_query_handler(text='createProfile')
async def check_user_from_db(message: types.Message):
    cur.execute("SELECT user_id FROM people WHERE user_id=?", (message.from_user.id,))
    user = cur.fetchall()
    if not user:
        await bot.send_message(message.from_user.id, 'Отлично!👌 Для начала отправь фото профиля', reply_markup=cancel_kb())
        await ProfileStatesGroup.photo.set()
    else:
        await bot.send_message(message.from_user.id, '🙅‍♂️ Вы уже зарегистрированы')


@dp.message_handler(lambda message: not message.photo, state=ProfileStatesGroup.photo)
async def check_photo(message: types.Message):
    await message.reply('Это не фото ❌')


@dp.message_handler(content_types=['photo'], state=ProfileStatesGroup.photo)
async def load_photo(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id

    await message.delete()
    await message.answer('Теперь отправь никнейм')
    await ProfileStatesGroup.next()


@dp.message_handler(lambda message: message.text.isdigit(), state=ProfileStatesGroup.name)
async def check_name(message: types.Message):
    await message.delete()
    await message.answer('Имя не должно состоять из цифр ❌')


@dp.message_handler(state=ProfileStatesGroup.name)
async def load_name(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as data:
        data['name'] = message.text
        await create_profile(user_id=message.from_user.id)
        await bot.send_photo(message.from_user.id, photo=data['photo'], caption=f"Имя: {data['name']}\nID: {message.from_user.id}")

    await message.delete()
    await edit_profile(state, user_id=message.from_user.id)
    await message.answer('Профиль успешно создан ✅')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
