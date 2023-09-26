# user_data = {}
#
# @bot.message_handler(commands=['Войти'])
# def process_description_step(message):
#     try:
#         user_id = message.from_user.id
#         user = user_data[user_id]
#         user.description = message.text
#
#         # Проверка есть ли пользователь в БД
#         sql = "SELECT * FROM users WHERE user_id = {0}".format(user_id)
#         cursor.execute(sql)
#         existsUser = cursor.fetchone()
#
#         markup = types.ReplyKeyboardRemove(selective=False)
#         bot.send_message(message.chat.id, "Вы успешно вошли в базу бота")
#         bot.register_next_step_handler(msg, process_baza_step)
#     except Exception as e:
#         bot.reply_to(message, 'oooops')
#
#
# async def looked(self, user_id):
#     async with self.connection:
#         result = self.cur.execute("SELECT * FROM people WHERE user_id =?", (user_id,)).fetchall()


@dp.message_handler(state=QuizzesStatesGroup.main_question)
async def load_main_quest(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as new_data:
        new_data['main_question'] = message.text

    await message.reply('Отправь первый вариант ответа')
    await QuizzesStatesGroup.next()


@dp.message_handler(state=QuizzesStatesGroup.first_answer)
async def load_first_variant(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as new_data:
        new_data['first_answer'] = message.text

    await message.reply('Отправь второй вариант ответа')
    await QuizzesStatesGroup.next()


@dp.message_handler(state=QuizzesStatesGroup.second_answer)
async def load_second_variant(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as new_data:
        new_data['second_answer'] = message.text

    await message.reply('Отправь третий вариант ответа')
    await QuizzesStatesGroup.next()


@dp.message_handler(state=QuizzesStatesGroup.third_answer)
async def load_third_variant(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as new_data:
        new_data['third_answer'] = message.text

    await message.reply('Теперь отправь четвертый вариант ответа')
    await QuizzesStatesGroup.next()


@dp.message_handler(state=QuizzesStatesGroup.fourth_answer)
async def load_fourth_answer(message: types.Message, state: FSMContext) -> None:
    async with state.proxy() as new_data:
        new_data['fourth_answer'] = message.text
        await create_quiz()

    await edit_quiz(state)
    await message.reply('Вопрос был успешно создан')
    await state.finish()