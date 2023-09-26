import sqlite3 as sq
import random


async def db_start():
    global db, cur

    db = sq.connect('profile.db', timeout=30)
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS people(user_id TEXT PRIMARY KEY, photo TEXT, name TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS questions(question_id INTEGER PRIMARY KEY, main_question TEXT, first_answer TEXT, second_answer TEXT, third_answer TEXT, fourth_answer TEXT, correct_option)")
    cur.execute("CREATE TABLE IF NOT EXISTS active_users(id TEXT PRIMARY KEY)")

    db.commit()


async def create_profile(user_id):
    user = cur.execute("SELECT 1 FROM people WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO people VALUES(?, ?, ?)", (user_id, '', ''))
        db.commit()


async def edit_profile(state, user_id):
    async with state.proxy() as data:
        cur.execute("UPDATE people SET photo = '{}', name = '{}' WHERE user_id == '{}'".format(
            data['photo'], data['name'], user_id))
        db.commit()


async def create_active(user_id):
    active_user = cur.execute("SELECT 1 FROM active_users WHERE id == '{key}'".format(key=user_id)).fetchone()
    if not active_user:
        cur.execute("INSERT INTO active_users VALUES(?)", (user_id,))
        db.commit()


async def edit_active(state):
    async with state.proxy() as new_active_data:
        cur.execute("UPDATE questions SET id = '{}'".format(new_active_data['id']))
        db.commit()


async def create_quiz(state):
    async with state.proxy() as create_data:
        quest = cur.execute("INSERT INTO questions (main_question, first_answer, second_answer, third_answer, fourth_answer, correct_option) VALUES(?, ?, ?, ?, ?, ?)",
                    (create_data['main_question'], create_data['first_answer'], create_data['second_answer'], create_data['third_answer'], create_data['fourth_answer'], create_data['correct_option']))
        db.commit()

    return quest


async def edit_quiz(state):
    async with state.proxy() as new_data:
        cur.execute("UPDATE questions SET main_question = '{}', first_answer = '{}', second_answer = '{}', "
                    "third_answer = '{}', fourth_answer = '{}', correct_option = '{}'".format(
                     new_data['main_question'], new_data['first_answer'], new_data['second_answer'], new_data['third_answer'], new_data['fourth_answer'], new_data['correct_option']))
        db.commit()


def save_user_selected_answer(question_id, user_answer_index):
    cur.execute('UPDATE questions SET user_selected_answer = ? WHERE id = ?', (user_answer_index, question_id))

    db.commit()


def get_correct_answer_index(question_id):
    cur.execute('SELECT correct_option FROM questions WHERE question_id = ?', (question_id,))
    row = cur.fetchone()
    if row:
        correct_answer_index = row[0]
        return correct_answer_index
    else:
        return None


def get_all_info_in_questions(question_id):
    cur.execute("SELECT * FROM questions WHERE correct_option =?", (question_id,))
    all_info = cur.fetchone()

    return all_info


async def create_state(state):
    async with state.proxy() as state_data:
        create = cur.execute("INSERT INTO is_state VALUES(?, ?, ?, ?)",
                    (state_data['first_st'], state_data['second_st'], state_data['third_st'], state_data['fourth_st']))
        db.commit()

    return create


async def edit_state(state):
    async with state.proxy() as new_st_data:
        cur.execute("UPDATE is_state SET first_st = '{}', second_st = '{}', third_st = '{}', fourth_st = '{}'".format(
                     new_st_data['first_st'], new_st_data['second_st'], new_st_data['third_st'], new_st_data['fourth_st']))
        db.commit()


async def get_state():
    all_state = cur.execute("SELECT * FROM is_state").fetchall()

    return all_state


async def get_all_users():

    users = cur.execute("SELECT * FROM people").fetchall()

    return users


async def get_someone_question():

    quizzes = cur.execute("SELECT * FROM questions").fetchall()

    return quizzes


async def get_all_answer():
    all_answers = cur.execute("SELECT * FROM questions").fetchall()

    return all_answers


async def get_all_quest(questions):
    cur.execute(f"SELECT * FROM questions ORDER BY RANDOM() LIMIT 1")
    random_quest = cur.fetchone()

    if random_quest:
        question_data = {
            'question_id': random_quest[0],
            'main_question': random_quest[1],
            'first_answer': random_quest[2],
            'second_answer': random_quest[3],
            'third_answer': random_quest[4],
            'fourth_answer': random_quest[5],
            'correct_option': random_quest[6]
        }
        return question_data

    return None  # Возвращаем None, если случайный вопрос не найден



async def get_all_question():
    all_quest = cur.execute("SELECT main_question FROM questions").fetchall()

    return all_quest


async def get_question_id(state, question_id):
    get_index_quest = cur.execute("SELECT question_id FROM questions WHERE question_id =?", (question_id))

    return get_index_quest


async def get_info(state):
    global question_text, options
    get_all_information = cur.execute("SELECT * FROM questions")
    for gai in get_all_information:
        question_text = gai[1]
        options = [gai[2], gai[3], gai[4], gai[5]]
    return {'text': question_text, 'options': options}


def get_question_info(question_id):
    cur.execute("SELECT main_question, first_answer, second_answer, third_answer, fourth_answer, correct_option FROM user_questions WHERE question_id = ?",
                   (question_id,))
    question_info = cur.fetchone()

    return question_info
