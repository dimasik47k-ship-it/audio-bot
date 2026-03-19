import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from config import BOT_TOKEN, TEMP_DIR
from handlers import register_handlers
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройки
TOKEN = BOT_TOKEN
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 8000))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", f"https://audio-bot-886e.onrender.com")  # Твой URL на Render

# Роутер для бота
router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🎧 **AudioTool Bot**\n\nОтправь аудиофайл для обработки!", parse_mode="Markdown")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("✏️ Теги | 🎨 Обложка | 🔄 Конвертация | 🗑️ Очистка", parse_mode="Markdown")

# Lifespan для правильного запуска/остановки
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём папку temp
    Path(TEMP_DIR).mkdir(exist_ok=True)
    
    # Инициализируем бота и диспетчер
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    # Регистрируем хендлеры
    register_handlers(dp)
    dp.include_router(router)
    
    # Устанавливаем webhook
    await bot.set_webhook(f"{WEBHOOK_URL}/bot", drop_pending_updates=True)
    logger.info(f"Webhook установлен: {WEBHOOK_URL}/bot")
    
    # Сохраняем в state
    app.state.bot = bot
    app.state.dp = dp
    
    logger.info("🤖 Бот запущен!")
    yield
    
    # Очистка при остановке
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()
    logger.info("🤖 Бот остановлен")

# FastAPI приложение
app = FastAPI(lifespan=lifespan)

# Эндпоинты для здоровья
@app.get("/")
async def root():
    return {"status": "ok", "service": "AudioTool Bot"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

# Обработчик вебхука от Telegram
@app.post("/bot")
async def telegram_webhook(request: Request):
    bot: Bot = app.state.bot
    data = await request.json()
    update = Update(**data)
    dp: Dispatcher = app.state.dp
    asyncio.create_task(dp.feed_update(bot, update))
    return {"ok": True}

# Настройка обработчика запросов
def setup_webhook(app: web.Application, dp: Dispatcher, bot: Bot):
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/bot")
    setup_application(app, dp, bot=bot)

# Запуск
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=WEBAPP_HOST, port=WEBAPP_PORT)