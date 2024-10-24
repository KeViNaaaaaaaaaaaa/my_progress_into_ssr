from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart

import keyboards as kb
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import sqlite3
from keyboards import (text_connect, word_connect, text_cache, word_cache, save_name_connect, name_cache,
                       login_connect, login_cache)
from search_filters import search_word_in_text, fuzzy_search
from file_input import get_file_content
import re
from create_bot import bot

routers = Router()


def check_auth(func):
    async def wrapped(callback_or_message, *args, state=None, **kwargs):
        user_data = await state.get_data()
        login = user_data.get('login')

        if not login:
            await callback_or_message.answer('Вы не авторизованы! Пожалуйста, войдите в аккаунт или зарегистрируйтесь.',
                                             reply_markup=kb.inline_keyboard3)
        await func(callback_or_message, *args, state=state, **kwargs)

    return wrapped


class AuthForm(StatesGroup):
    login = State()
    password = State()
    save_name = State()


class Form(StatesGroup):
    get_save_name = State()
    text = State()
    word = State()
    save_name = State()
    unrecognized = State()
    save_file = State()
    text_to_replace = State()
    replacement = State()
    replacement_choice = State()


class SearchOptions(StatesGroup):
    case_sensitive = State()
    fuzzy_search = State()
    choice_output = State()
    choice_change = State()


class Search(StatesGroup):
    builder_for = State()
    results = State()
    texts_selection = State()
    file_selection = State()
    word_selection = State()
    choice_selection = State()
    file_upload = State()
    word_input = State()
    replace_confirmation = State()


async def connect_db():
    return sqlite3.connect('SearchBot1.db')


async def user_exists(login):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE login = ?", (login,))
    user = cur.fetchone()
    conn.close()
    return user


async def login_user(login, password):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE login = ? AND password = ?", (login, password))
    user = cur.fetchone()
    conn.close()
    return user


async def register_user(user_id, login, password):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, login, password) VALUES (?, ?, ?)", (user_id, login, password))
    conn.commit()
    conn.close()


async def get_login(login):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("SELECT login FROM 'users' WHERE login = ?", (login,))
    user = cur.fetchall()
    await login_connect(user)
    conn.close()
    return user


async def del_login(login):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM save_text_word WHERE login = ?", (login,))
    cur.execute("DELETE FROM user_text WHERE login = ?", (login,))
    cur.execute("DELETE FROM user_word WHERE login = ?", (login,))
    cur.execute("DELETE FROM users WHERE login = ?", (login,))
    conn.commit()
    conn.close()


async def save_text_word(login, save_name, save):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO save_text_word (login, save_name, save) VALUES (?, ?, ?)", (login, save_name, save))
    conn.commit()
    conn.close()


async def del_word(word, login):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM user_word WHERE word = ? AND login = ?", (word, login))
    conn.commit()
    conn.close()


async def del_save(save_name, login):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM save_text_word WHERE save_name = ? AND login = ?", (save_name, login))
    conn.commit()
    conn.close()


async def del_text(text, login):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM user_text WHERE text = ? AND login = ?", (text, login))
    conn.commit()
    conn.close()


async def replace_text(modified_text, login, text):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("""UPDATE user_text SET text = ? WHERE login = ? AND text = ?""", (modified_text, login, text))
    conn.commit()
    conn.close()


async def get_text_word(login):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("SELECT save_name FROM save_text_word WHERE login = ?", (login,))
    user = cur.fetchall()
    print(user)
    await save_name_connect(user)
    conn.close()
    return user


async def get_save_text(save_name):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("SELECT save FROM save_text_word WHERE save_name = ?", (save_name,))
    user = cur.fetchone()
    conn.close()
    return user[0]


async def add_text(login, text):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO user_text (login, text) VALUES (?, ?)", (login, text))
    conn.commit()
    conn.close()


async def add_word(login, word):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO user_word (login, word) VALUES (?, ?)", (login, word))
    conn.commit()
    conn.close()


async def get_text(login):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("SELECT text FROM 'user_text' WHERE login = ?", (login,))
    user = cur.fetchall()
    await text_connect(user)
    conn.close()
    return user


async def get_word(login):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("SELECT word FROM 'user_word' WHERE login = ?", (login,))
    user = cur.fetchall()
    await word_connect(user)
    conn.close()
    return user


async def check_user_accounts(user_id):
    conn = await connect_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE user_id = ?", (user_id,))
    account_count = cur.fetchone()[0]
    conn.close()
    return account_count >= 5


async def check_accounts_text(login):
    conn = await connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM user_text WHERE login = ?", (login,))
    text_count = cur.fetchone()[0]

    conn.close()

    return text_count >= 10


async def check_accounts_word(login):
    conn = await connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM user_word WHERE login = ?", (login,))
    word_count = cur.fetchone()[0]

    conn.close()

    return word_count >= 10


@routers.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Добро пожаловать! Выберите действие:', reply_markup=kb.main)
    await state.set_state(Form.unrecognized)


@routers.message(lambda message: message.text == 'Меню')
async def handle_menu(message: Message, state: FSMContext):
    await message.answer('Главное меню бота', reply_markup=kb.inline_keyboard)
    await state.set_state(Form.unrecognized)


@routers.message(lambda message: message.text == 'Вход')
async def handle_login(message: Message, state: FSMContext):
    await message.answer('Войдите в аккаунт или зарегистрируйте новый', reply_markup=kb.inline_keyboard3)
    await state.set_state(Form.unrecognized)


@routers.message(lambda message: message.text == 'Поиск')
@check_auth
async def handle_search(message: Message, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    await get_text_word(login)
    if not await get_text_word(login):
        await message.answer('У вас нет текстов для поиска.')
    else:
        await message.answer('Выберите текст', reply_markup=kb.builder2.as_markup())
    await state.set_state(Form.unrecognized)


@routers.message(lambda message: message.text == 'Сохранения')
@check_auth
async def handle_saves(message: Message):
    await message.answer("Ваши сохранения:")


@routers.message(lambda message: message.text == 'Удалить аккаунт')
@check_auth
async def handle_delete_account(message: Message):
    await message.answer("Вы уверены, что хотите удалить аккаунт?")


@routers.callback_query(F.data == 'register')
async def ask_for_text(callback: CallbackQuery, state: FSMContext):
    action = callback.data
    user_id = callback.from_user.id
    if await check_user_accounts(user_id):
        await callback.message.answer("Вы не можете зарегистрировать более 5 аккаунтов.")
    else:
        await state.update_data(action=action)
        await callback.message.answer('Добро пожаловать! Для начала введите логин:')
        await state.set_state(AuthForm.login)


@routers.callback_query(F.data == 'back')
async def ask_for_back(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    if not login:
        await callback.message.answer('Добро пожаловать! Выберите действие:', reply_markup=kb.inline_keyboard3)
    else:
        await callback.message.answer('Вы в аккаунте', reply_markup=kb.inline_keyboard)


@routers.callback_query(F.data == 'login')
async def ask_for_login(callback: CallbackQuery, state: FSMContext):
    action = callback.data
    await state.update_data(action=action)
    await callback.message.answer('Добро пожаловать! Для начала введите логин:')
    await state.set_state(AuthForm.login)


@routers.message(AuthForm.login)
async def ask_for_password(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer('Введите пароль:')
    await state.set_state(AuthForm.password)


@routers.message(AuthForm.password)
async def authorize(message: Message, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    password = message.text
    action = user_data['action']
    if action == 'login':
        if await login_user(login, password):
            await state.update_data(password=password)
            await message.answer('Вы успешно авторизованы! Выберите действие:', reply_markup=kb.inline_keyboard)
        else:
            await message.answer('Неверные логин или пароль. Попробуйте снова.', reply_markup=kb.inline_keyboard4)
            await state.clear()
    if action == 'register':
        if await user_exists(login):
            await message.answer('Аккаунт с таким логином уже существует.', reply_markup=kb.inline_keyboard4)
            await state.clear()
        else:
            await register_user(user_id=message.from_user.id, login=login, password=password)
            await message.answer('Регистрация завершена! Теперь можете выбрать действие.',
                                 reply_markup=kb.inline_keyboard3)
            await state.clear()
    await state.set_state(Form.unrecognized)


@routers.callback_query(F.data == 'view_data')
@check_auth
async def search_texts(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    await get_text_word(login)
    if not await get_text_word(login):
        await callback.message.answer('У вас нет текстов для поиска.')
    else:
        await callback.message.answer('Выберите текст', reply_markup=kb.builder2.as_markup())
    await state.set_state(Form.unrecognized)


@routers.callback_query(lambda c: c.data.startswith('name:'))
@check_auth
async def on_text_choice(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    builder_for = user_data.get('builder_for')
    save_name = user_data.get('save_name')
    name_hash = callback.data.split(":")[1]
    await state.update_data(name_hash=name_hash)
    full_name = name_cache.get(name_hash)
    text = await get_save_text(full_name)
    if builder_for == 'search':
        sentences = re.split(r'(?<=[.!?])\s*', text)
        print(text, full_name, name_hash, save_name)
        for i in sentences:
            await callback.message.answer(i)
        await state.set_state(Form.unrecognized)
    else:
        await del_save(full_name, login)
        await callback.message.answer(f"Вы удалили сохранение: {full_name}", reply_markup=kb.inline_keyboard_next)


@routers.callback_query(F.data == 'name')
@check_auth
async def ask_for_text_input(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите текст:')
    await state.set_state(Form.text)


@routers.callback_query(F.data == 'name1')
@check_auth
async def ask_for_word(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите слово:')
    await state.set_state(Form.word)


#
# @routers.message(Form.text)
# async def receive_text(message: Message, state: FSMContext):
#     await state.update_data(text=message.text)
#     await message.answer('Введите слово:')
#     await state.set_state(Form.word)


@routers.message(Form.word)
@check_auth
async def receive_word(message: Message, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    word = message.text
    if await check_accounts_word(login):
        await message.answer("Вы не можете записать более 10 слов.", reply_markup=kb.inline_keyboard)
    else:
        await add_word(login, word)
        await message.answer(f"слово успешно записано", reply_markup=kb.inline_keyboard)
    await state.set_state(Form.unrecognized)


@routers.message(Form.text)
@check_auth
async def receive_text(message: Message, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    text = message.text
    if await check_accounts_text(login):
        await message.answer("Вы не можете записать более 10 текстов.", reply_markup=kb.inline_keyboard)
    else:
        await add_text(login, text)
        await message.answer(f"Текст успешно записан", reply_markup=kb.inline_keyboard)
    await state.set_state(Form.unrecognized)


@routers.callback_query(F.data == 'bjob')
@check_auth
async def save_text(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Выберите, по чему вы хотите искать:', reply_markup=kb.inline_search_type)
    await state.set_state(Form.unrecognized)


@routers.callback_query(F.data == 'search_texts')
@check_auth
async def search_texts(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()

    login = user_data.get('login')
    await get_text(login)
    if not await get_text(login):
        await callback.message.answer('У вас нет текстов для поиска.')
    else:
        await callback.message.answer('Выберите текст', reply_markup=kb.builder.as_markup())


@routers.callback_query(F.data == 'search_files')
@check_auth
async def search_files(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Пожалуйста, отправьте файл для поиска:')
    await state.set_state(Search.file_upload)


@routers.message(F.document)
@check_auth
async def receive_files_for_search(message: Message, state: FSMContext):
    user_data = await state.get_data()
    uploaded_files = user_data.get('uploaded_files', [])
    uploaded_files.append(message.document.file_id)
    await state.update_data(uploaded_files=uploaded_files)

    await message.answer('Файл загружен. Если хотите, загрузите еще один файл или введите слово для поиска:')
    await state.set_state(Search.word_input)


@routers.message(Search.word_input)
@check_auth
async def receive_search_word(message: Message, state: FSMContext):
    search_word = message.text
    user_data = await state.get_data()
    uploaded_files = user_data.get('uploaded_files', [])

    await state.update_data(full_word=search_word)

    if search_word and uploaded_files:

        results = ''
        for file_id in uploaded_files:
            file_content = await get_file_content(file_id)  # Ваша функция для получения содержимого файла

            if file_content:
                # results.append(f"Результаты для файла {file_id}: {found_sentences}")
                results += file_content

        else:
            await message.answer("По вашему запросу ничего не найдено в загруженных файлах.")
        await state.update_data(uploaded_files=[])
    else:
        await message.answer("Ошибка поиска. Попробуйте снова.")
    await state.update_data(full_text=results)

    await message.answer("Учитывать ли регистр при поиске?", reply_markup=kb.inline_keyboard7)
    await state.set_state(SearchOptions.case_sensitive)


@routers.callback_query(lambda c: c.data.startswith('text:'))
@check_auth
async def on_text_choice(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    builder_for = user_data.get('builder_for')
    text_hash = callback.data.split(":")[1]
    await state.update_data(text_hash=text_hash)
    full_text = text_cache.get(text_hash)
    await state.update_data(full_text=full_text)
    print(full_text)
    if builder_for == 'search':
        await callback.message.answer(f"Вы выбрали текст: {full_text}", reply_markup=kb.inline_keyboard5)
    if builder_for == 'replace':
        await callback.message.answer(f"Введите слово для замены")
        await state.set_state(Form.text_to_replace)
    else:
        await del_text(full_text, login)
        await callback.message.answer(f"Вы удалили слово: {full_text}", reply_markup=kb.inline_keyboard_next)


@routers.callback_query(F.data == 'next')
@check_auth
async def another_data(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    await get_word(login)
    await state.update_data(builder_for='search')
    await callback.message.answer('Выберите слово:', reply_markup=kb.builder1.as_markup())


@routers.callback_query(F.data == 'next1')
@check_auth
async def ask_case_sensitive(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Учитывать ли регистр при поиске?", reply_markup=kb.inline_keyboard7)
    await state.set_state(SearchOptions.case_sensitive)


@routers.callback_query(SearchOptions.case_sensitive, F.data == 'yes')
@check_auth
async def ask_fuzzy_search_yes(callback: CallbackQuery, state: FSMContext):
    await state.update_data(case_sensitive=True)
    await callback.message.answer("Использовать ли неточный поиск (учет ошибок в 1-3 символах)?",
                                  reply_markup=kb.inline_keyboard7)
    await state.set_state(SearchOptions.fuzzy_search)


@routers.callback_query(SearchOptions.case_sensitive, F.data == 'no')
@check_auth
async def ask_fuzzy_search_no(callback: CallbackQuery, state: FSMContext):
    await state.update_data(case_sensitive=False)
    await callback.message.answer("Использовать ли неточный поиск (учет ошибок в 1-3 символах)?",
                                  reply_markup=kb.inline_keyboard7)
    await state.set_state(SearchOptions.fuzzy_search)


@routers.callback_query(SearchOptions.fuzzy_search, F.data == 'yes')
@check_auth
async def output_text(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    case_sensitive = user_data.get('case_sensitive')
    full_text = user_data.get('full_text')
    full_word = user_data.get('full_word')

    results = await fuzzy_search(full_text, full_word, case_sensitive=case_sensitive)
    await state.update_data(results=results)
    print(results)
    if results != list():
        await callback.message.answer("Каким образом вывести текст?",
                                      reply_markup=kb.inline_out_type)
        await state.set_state(SearchOptions.choice_output)
    else:
        await callback.message.answer("Результаты не найдены.")


@routers.callback_query(SearchOptions.fuzzy_search, F.data == 'no')
@check_auth
async def output_file(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    case_sensitive = user_data.get('case_sensitive')
    full_text = user_data.get('full_text')
    full_word = user_data.get('full_word')

    results = await search_word_in_text(full_text, full_word, case_sensitive=case_sensitive)
    await state.update_data(results=results)
    print(results, case_sensitive)
    if results != list():
        await callback.message.answer("Каким образом вывести текст?",
                                      reply_markup=kb.inline_out_type)
        await state.set_state(SearchOptions.choice_output)
    else:
        await callback.message.answer("Результаты не найдены.")


@routers.message(Form.save_file)
@check_auth
async def input_file(message: Message, state: FSMContext):
    name_file = message.text
    await state.update_data(name_file=name_file)
    await message.answer('Вы ввели название файла', reply_markup=kb.inline_keyboard8)


@routers.callback_query(F.data == 'next2')
@check_auth
async def output_real_file(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    name_file = user_data.get('name_file')
    results = user_data.get('results')
    with open(f"{name_file}.txt", 'w+', encoding='utf-8') as f:
        for i in results:
            f.write(f'{i}\n')
    document = FSInputFile(f"{name_file}.txt")
    await bot.send_document(callback.message.chat.id, document)
    await callback.message.answer("Файл успешно отправлен!")


@routers.callback_query(F.data == 'become2')
@check_auth
async def back_name_file(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('ВВедите название файла:')
    await state.set_state(Form.save_file)


@routers.callback_query(SearchOptions.choice_output, F.data == 'texts')
@check_auth
async def perform_fuzzy_search(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    results = user_data.get('results')

    for result in results:
        await callback.message.answer(result)
    await callback.message.answer("Сохранить результат поиска?", reply_markup=kb.inline_keyboard7)
    await state.set_state(Form.save_name)


@routers.callback_query(SearchOptions.choice_output, F.data == 'files')
@check_auth
async def perform_exact_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите название файла:')
    await state.set_state(Form.save_file)


@routers.callback_query(Form.save_name, F.data == 'no')
@check_auth
async def perform_exact_search(callback: CallbackQuery):
    await callback.message.answer('Ничего не выбрано! Пожалуйста, выберите действие с помощью кнопок.',
                                  reply_markup=kb.inline_keyboard)


@routers.callback_query(Form.save_name, F.data == 'yes')
@check_auth
async def perform_exact_search(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    results = user_data.get('results')

    print(results)
    save_data = ' '.join(results)
    print(save_data)
    await state.update_data(save_data=save_data)
    await callback.message.answer("Введите имя для сохранения результата:")

    await state.set_state(Form.get_save_name)


@routers.message(Form.get_save_name)
@check_auth
async def save_search_results(message: Message, state: FSMContext):
    save_name = message.text

    user_data = await state.get_data()
    login = user_data.get('login')
    save_data = user_data.get('save_data')

    await save_text_word(login, save_name, save_data)

    await message.answer(f"Результаты сохранены под именем: {save_name}")

    await state.set_state(Form.unrecognized)


@routers.callback_query(F.data == 'become')
@check_auth
async def back_text(callback: CallbackQuery):
    await callback.message.answer('Выберите текст', reply_markup=kb.builder.as_markup())


@routers.callback_query(F.data == 'become1')
@check_auth
async def back_word(callback: CallbackQuery):
    await callback.message.answer('Выберите слово', reply_markup=kb.builder1.as_markup())


@routers.callback_query(lambda c: c.data.startswith('word:'))
@check_auth
async def on_word_choice(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    builder_for = user_data.get('builder_for')
    word_hash = callback.data.split(":")[1]
    await state.update_data(word_hash=word_hash)
    full_word = word_cache.get(word_hash)
    await state.update_data(full_word=full_word)
    if builder_for == 'search':
        await callback.message.answer(f"Вы выбрали слово: {full_word}", reply_markup=kb.inline_keyboard6)
    else:
        await del_word(full_word, login)
        await callback.message.answer(f"Вы удалили слово: {full_word}", reply_markup=kb.inline_keyboard_next)


@routers.callback_query(F.data == 'logout')
@check_auth
async def logout(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer('Вы вышли из аккаунта', reply_markup=kb.inline_keyboard3)
    await state.set_state(Form.unrecognized)


@routers.callback_query(F.data == 'yet')
@check_auth
async def logout(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Вы перешли на следующую страницу', reply_markup=kb.inline_keyboard_next)
    await state.set_state(Form.unrecognized)


@routers.callback_query(F.data == 'main')
@check_auth
async def logout(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Вы вернулись обратно на главную страницу', reply_markup=kb.inline_keyboard)
    await state.set_state(Form.unrecognized)


@routers.callback_query(F.data == 'text_interact')
@check_auth
async def logout(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Выберите действие', reply_markup=kb.inline_keyboard_interact)
    await state.set_state(Form.unrecognized)


@routers.callback_query(F.data == 'del')
@check_auth
async def logout(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    await state.update_data(builder_for='del')
    await get_text(login)
    await callback.message.answer('Выберите действие', reply_markup=kb.builder.as_markup())


@routers.callback_query(F.data == 'change')
@check_auth
async def on_replace_request(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    await state.update_data(builder_for='replace')
    await get_text(login)
    await callback.message.answer('Введите текст, который хотите заменить:', reply_markup=kb.builder.as_markup())


@routers.message(Form.text_to_replace)
@check_auth
async def on_text_to_replace_received(message: Message, state: FSMContext):
    await state.update_data(text_to_replace=message.text)
    await message.answer('Введите новое значение для замены:')
    await state.set_state(Form.replacement)


@routers.message(Form.replacement)
@check_auth
async def on_replacement_received(message: Message, state: FSMContext):
    await state.update_data(replacement_value=message.text)
    await message.answer('Выберите, как хотите произвести замену:', reply_markup=kb.replace_choice_keyboard)


@routers.callback_query(lambda c: c.data.startswith('replace_'))
@check_auth
async def on_replacement_choice(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    full_text = user_data.get('full_text')
    text_to_replace = user_data.get('text_to_replace')
    replacement_value = user_data.get('replacement_value')

    if callback.data == "replace_all":
        modified_text = full_text.replace(text_to_replace, replacement_value)
    elif callback.data == "replace_first":
        modified_text = full_text.replace(text_to_replace, replacement_value, 1)
    elif callback.data == "replace_last":
        parts = full_text.rsplit(text_to_replace, 1)
        modified_text = replacement_value.join(parts)

    await replace_text(modified_text, login, full_text)

    await callback.message.answer(f"Замена выполнена: {modified_text}", reply_markup=kb.inline_keyboard_next)


@routers.callback_query(F.data == 'word_interact')
@check_auth
async def logout(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    await state.update_data(builder_for='del')
    await get_word(login)
    await callback.message.answer('Выберите действие', reply_markup=kb.builder1.as_markup())


@routers.callback_query(F.data == 'save_del')
@check_auth
async def logout(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    await state.update_data(builder_for='del')
    await get_text_word(login)
    await callback.message.answer('Выберите действие', reply_markup=kb.builder2.as_markup())


@routers.callback_query(F.data == 'login_interact')
@check_auth
async def logout(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    await get_login(login)
    await callback.message.answer('Выберите действие', reply_markup=kb.builder3.as_markup())


@routers.callback_query(lambda c: c.data.startswith('login:'))
@check_auth
async def on_text_choice(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    login = user_data.get('login')
    login_hash = callback.data.split(":")[1]
    await state.update_data(login_hash=login_hash)
    full_login = login_cache.get(login_hash)
    await state.update_data(full_login=full_login)
    print(full_login, login)
    if login == full_login:
        await callback.message.answer('Нельзя удалить аккаунт на котором находишься.',
                                      reply_markup=kb.inline_keyboard_next)
    else:
        await del_login(login)
        await callback.message.answer(f"Вы удалили аккаунт: {login}", reply_markup=kb.inline_keyboard_next)


@routers.message(Form.unrecognized)
async def handle_unrecognized_message(message: Message):
    await message.answer('Ничего не выбрано! Пожалуйста, выберите действие с помощью кнопок.')
