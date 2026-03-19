import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Update
from config import BOT_TOKEN, TEMP_DIR
from handlers import register_handlers
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Настройки
TOKEN = BOT_TOKEN
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://audio-bot-886e.onrender.com")

# Роутер для простых команд
router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🎧 **AudioTool Bot**\n\n"
        "Отправь аудиофайл для обработки!",
        parse_mode="Markdown"
    )

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "✏️ Теги | 🎨 Обложка | 🔄 Конвертация | 🗑️ Очистка",
        parse_mode="Markdown"
    )

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
    logger.info(f"✅ Webhook установлен: {WEBHOOK_URL}/bot")
    
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

# ========== ЭНДПОИНТЫ ДЛЯ UPTIMEROBOT ==========

# Корневой путь (поддерживает и GET, и HEAD)
@app.get("/")
@app.head("/")
async def root():
    return {"status": "ok", "service": "AudioTool Bot"}

# Health check (поддерживает и GET, и HEAD)
@app.get("/health")
@app.head("/health")
async def health():
    return {"status": "healthy"}

# ========== ВЕБХУК TELEGRAM ==========

@app.post("/bot")
async def telegram_webhook(request: Request):
    bot: Bot = app.state.bot
    data = await request.json()
    update = Update(**data)
    dp: Dispatcher = app.state.dp
    asyncio.create_task(dp.feed_update(bot, update))
    return {"ok": True}

# Запуск
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=WEBAPP_HOST, port=WEBAPP_PORT)