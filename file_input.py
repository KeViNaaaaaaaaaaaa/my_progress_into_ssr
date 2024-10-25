from create_bot import bot
from config import TOKEN
import aiohttp


async def download_file(file_id, file_name):
    file = await bot.get_file(file_id)
    file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file.file_path}'
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            with open(file_name, 'wb') as f:
                f.write(await resp.read())


async def get_file_content(file_id):
    file_name = "downloaded_file"
    await download_file(file_id, file_name)
    with open(file_name, 'r', encoding='utf-8') as f:
        return f.read()
