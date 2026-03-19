from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from utils.ui import main_menu_kb
from utils.audio_processor import get_audio_info

router = Router()

@router.message(F.audio | F.voice | F.document)
async def handle_file(message: types.Message, state: FSMContext):
    file = message.audio or message.voice or message.document
    
    if not file:
        return
    
    # Проверка типа файла
    allowed_extensions = ('.mp3', '.flac', '.m4a', '.aac', '.wav', '.ogg', '.opus', '.wma')
    if file.file_name and not file.file_name.lower().endswith(allowed_extensions):
        if not file.mime_type or not file.mime_type.startswith('audio/'):
            await message.answer("❌ Это не аудиофайл. Отправь музыку! 🎵")
            return
    
    # Скачивание файла
    status_msg = await message.answer("⏳ Скачиваю файл...")
    
    file_info = await message.bot.get_file(file.file_id)
    file_path = file_info.file_path
    local_path = f"temp/{file_path.split('/')[-1]}"
    
    await message.bot.download_file(file_path, local_path)
    
    await state.update_data(
        file_path=local_path,
        original_name=file.file_name,
        file_id=file.file_id
    )
    
    # Получаем информацию о файле
    info = get_audio_info(local_path)
    
    text = f"🎵 **Файл получен!**\n\n"
    text += f"📁 Название: `{file.file_name}`\n"
    text += f"⏱ Длительность: {info.get('duration', 0):.1f} сек\n"
    
    if info.get('tags', {}).get('title'):
        text += f"🏷️ Трек: {info['tags'].get('title', 'Неизвестно')}\n"
        text += f"🎤 Артист: {info['tags'].get('artist', 'Неизвестно')}\n"
    else:
        text += f"🏷️ Теги: **Не найдены**\n"
    
    text += f"\n**Что будем делать?** 👇"
    
    await status_msg.edit_text(text, parse_mode="Markdown", reply_markup=main_menu_kb())

def register_file_handlers(dp):
    dp.include_router(router)