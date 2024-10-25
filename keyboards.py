from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import hashlib

builder = InlineKeyboardBuilder()
builder1 = InlineKeyboardBuilder()
builder2 = InlineKeyboardBuilder()
builder3 = InlineKeyboardBuilder()


async def hash_text(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:10]


text_cache = {}


async def text_connect(text):
    global builder
    builder = InlineKeyboardBuilder()

    for i in text:
        text_hash = await hash_text(i[0])
        text_cache[text_hash] = i[0]
        builder.add(InlineKeyboardButton(text=i[0][:10], callback_data=f'text:{text_hash}'))


async def word_connect(word):
    global builder1
    builder1 = InlineKeyboardBuilder()

    for i in word:
        builder1.add(InlineKeyboardButton(text=i[0], callback_data=f'word:{i[0]}'))


async def save_name_connect(name):
    global builder2
    builder2 = InlineKeyboardBuilder()

    for i in name:
        builder2.add(InlineKeyboardButton(text=i[0], callback_data=f'name:{i[0]}'))


async def login_connect(login):
    global builder3
    builder3 = InlineKeyboardBuilder()

    for i in login:
        builder3.add(InlineKeyboardButton(text=i[0], callback_data=f'login:{i[0]}'))


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Меню')],
    [KeyboardButton(text='Вход')],
    [KeyboardButton(text='Поиск')],
    [KeyboardButton(text='Сохранения')],
    [KeyboardButton(text='Удалить аккаунт')]
])

inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Записать текст', callback_data='name')],
    [InlineKeyboardButton(text='Записать слово', callback_data='name1')],
    [InlineKeyboardButton(text='Просмотреть результаты поиска', callback_data='view_data')],
    [InlineKeyboardButton(text='Выйти из аккаунта', callback_data='logout')],
    [InlineKeyboardButton(text='Поиск', callback_data='bjob')],
    [InlineKeyboardButton(text='Следующая страница', callback_data='yet')]
])

inline_keyboard_next = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Взаимодействовать с текстом', callback_data='text_interact')],
    [InlineKeyboardButton(text='Удалить слово', callback_data='word_interact')],
    [InlineKeyboardButton(text='Удалить аккаунт', callback_data='login_interact')],
    [InlineKeyboardButton(text='Удалить сохранение', callback_data='save_del')],
    [InlineKeyboardButton(text='Предыдущая страница', callback_data='main')]
])

inline_keyboard_interact = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Удалить', callback_data='del')],
    [InlineKeyboardButton(text='Произвести замену', callback_data='change')]
])

inline_keyboard3 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Войти", callback_data="login")],
    [InlineKeyboardButton(text="Регистрация", callback_data="register")]
])

inline_keyboard4 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="back")]
])

inline_keyboard5 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Далее", callback_data="next")],
    [InlineKeyboardButton(text="Назад", callback_data="become")]
])

inline_keyboard6 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Далее", callback_data="next1")],
    [InlineKeyboardButton(text="Назад", callback_data="become1")]
])

inline_keyboard7 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Да", callback_data="yes")],
    [InlineKeyboardButton(text="Нет", callback_data="no")]
])

inline_search_type = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Обычный поиск", callback_data="search_texts")],
    [InlineKeyboardButton(text="Поиск по файлу", callback_data="search_files")],
])

inline_out_type = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Обычный вывод", callback_data="texts")],
    [InlineKeyboardButton(text="Вывод файлом", callback_data="files")],
])

inline_keyboard8 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Далее", callback_data="next2")],
    [InlineKeyboardButton(text="Назад", callback_data="become2")]
])

replace_choice_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Заменить все", callback_data="replace_all")],
    [InlineKeyboardButton(text="Заменить первое", callback_data="replace_first")],
    [InlineKeyboardButton(text="Заменить последнее", callback_data="replace_last")]
])
