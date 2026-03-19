# Этот файл теперь не нужен для запуска на Render
# Но оставь для локального тестирования

import asyncio
import logging
from pathlib import Path
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties
from config import BOT_TOKEN, BOT_API_URL, TEMP_DIR
from handlers import register_handlers
from utils.ui import help_text

logging.basicConfig(level=logging.INFO)

if BOT_API_URL:
    session = AiohttpSession(api_url=BOT_API_URL)
    bot = Bot(token=BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode="Markdown"))
else:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))

dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🎧 **AudioTool Bot**\n\n"
        "Отправь мне **аудиофайл** — и я помогу:\n\n"
        "• ✏️ Изменить теги\n"
        "• 🔄 Конвертировать формат\n"
        "• 🎨 Добавить обложку\n"
        "• 🗑️ Очистить теги\n\n"
        "_🆓 Полностью бесплатно!_",
        parse_mode="Markdown"
    )

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(help_text())

async def cleanup_temp():
    while True:
        try:
            now = datetime.now()
            for f in TEMP_DIR.glob("*"):
                if f.is_file():
                    file_time = datetime.fromtimestamp(f.stat().st_mtime)
                    if now - file_time > timedelta(hours=1):
                        f.unlink()
                        logging.info(f"Deleted old: {f.name}")
            await asyncio.sleep(3600)
        except Exception as e:
            logging.error(f"Cleanup error: {e}")

async def main():
    register_handlers(dp)
    asyncio.create_task(cleanup_temp())
    logging.info("Бот запущен (локально)!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")
    finally:
        asyncio.run(bot.session.close())