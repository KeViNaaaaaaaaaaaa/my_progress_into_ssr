
from create_bot import bot
from config import TOKEN
from aiogram import types
import aiohttp
import os


async def download_file(file_id, file_name):
    file = await bot.get_file(file_id)
    file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file.file_path}'
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            with open(file_name, 'wb') as f:
                f.write(await resp.read())

    return file_name


async def get_file_content(file_id):
    file_name = "downloaded_file"
    downloaded_file = await download_file(file_id, file_name)
    with open(downloaded_file, 'r') as f:
        return f.read()