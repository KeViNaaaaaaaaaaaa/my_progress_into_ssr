import asyncio
import logging

from aiogram import Dispatcher
from routers import routers
from create_bot import bot
from aiogram_sqlite_storage.sqlitestore import SQLStorage
import sqlite3


async def connect_db():
    return sqlite3.connect('SearchBot1.db')


async def create_tables():
    conn = await connect_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        login TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS save_text_word (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT NOT NULL,
            save_name TEXT UNIQUE,
            save TEXT,
            FOREIGN KEY(login) REFERENCES users(login)
        )
        """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_text (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT NOT NULL,
        text TEXT,
        FOREIGN KEY(login) REFERENCES users(login)
    )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_word (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT NOT NULL,
            word TEXT,
            FOREIGN KEY(login) REFERENCES users(login)
        )
        """)

    conn.commit()
    conn.close()


async def main():
    await create_tables()

    my_storage = SQLStorage('SearchBot1.db', serializing_method='pickle')

    dp = Dispatcher(storage=my_storage)
    dp.include_router(routers)

    await dp.start_polling(bot)


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    try:
        asyncio.run(main(), debug=True)
    except KeyboardInterrupt:
        print('Бот завершил работу')
