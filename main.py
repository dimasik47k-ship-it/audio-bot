import asyncio
from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties
from config import BOT_TOKEN, TEMP_DIR
from handlers import register_handlers
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI приложение (для Keep-Alive)
app = FastAPI()

# Бот
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="Markdown"))
dp = Dispatcher()

# Регистрируем хендлеры
register_handlers(dp)

# Эндпоинт для здоровья (Render требует)
@app.get("/")
async def root():
    return {"status": "ok", "bot": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Запуск бота в фоне
async def start_bot():
    logger.info("Бот запущен!")
    await dp.start_polling(bot)

# Событие при старте FastAPI
@app.on_event("startup")
async def startup_event():
    # Создаём папку temp
    Path(TEMP_DIR).mkdir(exist_ok=True)
    # Запускаем бота в фоне
    asyncio.create_task(start_bot())

# Событие при остановке
@app.on_event("shutdown")
async def shutdown_event():
    await bot.session.close()
    logger.info("Бот остановлен")

# Для Render — запуск через uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)