from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.audio_processor import edit_tags, get_audio_info, clear_all_tags
from utils.ui import main_menu_kb, help_text
import time
import os

router = Router()

class TagEdit(StatesGroup):
    waiting_title = State()
    waiting_artist = State()
    waiting_album = State()
    waiting_year = State()
    waiting_genre = State()
    waiting_cover = State()

# ========== ГЛАВНОЕ МЕНЮ ==========

@router.callback_query(F.data == "edit_tags")
async def start_edit_tags(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get('file_path'):
        await callback.answer("❌ Файл не найден. Отправь аудиофайл сначала!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "✏️ **Редактирование тегов**\n\n"
        "Введите **название трека** (или нажмите /skip чтобы пропустить):",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip_title")]
        ])
    )
    await state.set_state(TagEdit.waiting_title)

@router.callback_query(F.data == "skip_title")
async def skip_title(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(title="")
    await callback.message.edit_text(
        "Введите **исполнителя** (или /skip):",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip_artist")]
        ])
    )
    await state.set_state(TagEdit.waiting_artist)

@router.message(TagEdit.waiting_title)
async def save_title(message: types.Message, state: FSMContext):
    if message.text == "/skip":
        await state.update_data(title="")
    else:
        await state.update_data(title=message.text)
    
    await message.answer(
        "Введите **исполнителя** (или /skip):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip_artist")]
        ])
    )
    await state.set_state(TagEdit.waiting_artist)

@router.callback_query(F.data == "skip_artist")
async def skip_artist(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(artist="")
    await goto_album(callback, state)

@router.message(TagEdit.waiting_artist)
async def save_artist(message: types.Message, state: FSMContext):
    if message.text == "/skip":
        await state.update_data(artist="")
    else:
        await state.update_data(artist=message.text)
    await goto_album(message, state)

async def goto_album(obj, state):
    await obj.answer(
        "Введите **альбом** (или /skip):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip_album")]
        ])
    )
    await state.set_state(TagEdit.waiting_album)

@router.callback_query(F.data == "skip_album")
@router.message(TagEdit.waiting_album)
async def save_album(obj, state: FSMContext):
    if hasattr(obj, 'text') and obj.text == "/skip":
        await state.update_data(album="")
    elif hasattr(obj, 'data'):
        await state.update_data(album="")
    elif hasattr(obj, 'text'):
        await state.update_data(album=obj.text)
    
    await obj.answer(
        "Введите **год** (или /skip):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip_year")]
        ])
    )
    await state.set_state(TagEdit.waiting_year)

@router.callback_query(F.data == "skip_year")
@router.message(TagEdit.waiting_year)
async def save_year(obj, state: FSMContext):
    if hasattr(obj, 'text') and obj.text == "/skip":
        await state.update_data(year="")
    elif hasattr(obj, 'data'):
        await state.update_data(year="")
    elif hasattr(obj, 'text'):
        await state.update_data(year=obj.text)
    
    await obj.answer(
        "Введите **жанр** (или /skip):",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip_genre")]
        ])
    )
    await state.set_state(TagEdit.waiting_genre)

@router.callback_query(F.data == "skip_genre")
@router.message(TagEdit.waiting_genre)
async def save_genre(obj, state: FSMContext):
    if hasattr(obj, 'text') and obj.text == "/skip":
        await state.update_data(genre="")
    elif hasattr(obj, 'data'):
        await state.update_data(genre="")
    elif hasattr(obj, 'text'):
        await state.update_data(genre=obj.text)
    
    await obj.answer(
        "🎨 Теперь отправьте **обложку** (картинку) или нажмите /skip:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏭ Пропустить обложку", callback_data="skip_cover")]
        ])
    )
    await state.set_state(TagEdit.waiting_cover)

@router.callback_query(F.data == "skip_cover")
async def skip_cover(callback: types.CallbackQuery, state: FSMContext):
    await process_and_send(callback.message, state, callback)

@router.message(TagEdit.waiting_cover, F.photo)
async def save_cover(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    cover_path = f"temp/cover_{message.from_user.id}_{int(time.time())}.jpg"
    
    await message.bot.download_file(file_info.file_path, cover_path)
    
    if os.path.exists(cover_path):
        await state.update_data(cover_path=cover_path)
        await process_and_send(message, state, message)
    else:
        await message.answer("❌ Ошибка сохранения обложки.")

@router.message(TagEdit.waiting_cover)
async def handle_cover_skip(message: types.Message, state: FSMContext):
    if message.text == "/skip":
        await process_and_send(message, state, message)

async def process_and_send(obj, state: FSMContext, original_obj):
    data = await state.get_data()
    file_path = data.get('file_path')
    
    if not file_path:
        await obj.answer("❌ Ошибка: файл не найден", show_alert=True)
        return
    
    status_msg = await obj.answer("⏳ Обрабатываю теги...")
    
    tags = {
        'title': data.get('title', ''),
        'artist': data.get('artist', ''),
        'album': data.get('album', ''),
        'date': data.get('year', ''),
        'genre': data.get('genre', '')
    }
    
    cover_path = data.get('cover_path')
    
    try:
        new_file = edit_tags(file_path, tags, cover_path)
        
        audio = types.FSInputFile(new_file)
        await obj.bot.send_audio(
            chat_id=obj.chat.id,
            audio=audio,
            title=(tags.get('title') or data.get('original_name', 'Unknown'))[:30],
            performer=(tags.get('artist') or 'Unknown')[:30],
            caption="✅ Готово! Теги обновлены.",
            parse_mode="Markdown"
        )
        
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(
            "❌ Ошибка обработки файла.\n"
            "Возможно, файл повреждён или формат не поддерживается.",
            parse_mode=None
        )
    
    await state.clear()
    await obj.answer("🎵 Отправь ещё файл или выбери действие:", reply_markup=main_menu_kb())

# ========== ДОПОЛНИТЕЛЬНЫЕ КНОПКИ ==========

@router.callback_query(F.data == "add_cover")
async def add_cover_only(callback: types.CallbackQuery, state: FSMContext):
    """Отдельная кнопка для добавления обложки"""
    data = await state.get_data()
    if not data.get('file_path'):
        await callback.answer("❌ Файл не найден. Отправь аудиофайл сначала!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🎨 **Добавление обложки**\n\n"
        "Отправьте картинку, которую хотите добавить в аудиофайл:",
        parse_mode="Markdown"
    )
    await state.set_state(TagEdit.waiting_cover)
    await state.update_data(cover_only=True)

@router.callback_query(F.data == "clear_tags")
async def clear_tags_only(callback: types.CallbackQuery, state: FSMContext):
    """Очистить все теги из файла"""
    data = await state.get_data()
    if not data.get('file_path'):
        await callback.answer("❌ Файл не найден. Отправь аудиофайл сначала!", show_alert=True)
        return
    
    status_msg = await callback.message.edit_text("🗑️ Очищаю теги...")
    
    try:
        file_path = data.get('file_path')
        new_file = clear_all_tags(file_path)
        
        audio = types.FSInputFile(new_file)
        await callback.message.bot.send_audio(
            chat_id=callback.message.chat.id,
            audio=audio,
            caption="✅ Теги очищены!"
        )
        
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(
            "❌ Ошибка очистки тегов.\n"
            "Возможно, в файле не было тегов.",
            parse_mode=None
        )
    
    await callback.message.answer("🎵 Готово! Отправь ещё файл:", reply_markup=main_menu_kb())

@router.callback_query(F.data == "help")
async def help_callback(callback: types.CallbackQuery):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    await callback.message.answer(
        "🎧 **AudioTool Bot — Помощь**\n\n"
        "**Возможности:**\n"
        "• ✏️ Редактирование тегов (название, артист, альбом, год, жанр)\n"
        "• 🎨 Добавление обложки в аудиофайл\n"
        "• 🔄 Конвертация между форматами (MP3, FLAC, WAV, M4A, OGG)\n"
        "• 🗑️ Очистка всех тегов\n\n"
        "**Поддерживаемые форматы:**\n"
        "MP3, FLAC, M4A, AAC, WAV, OGG, OPUS, WMA\n\n"
        "**Лимиты:**\n"
        "• До 50 МБ на файл (стандартный лимит Telegram)\n"
        "• Файлы удаляются через 1 час\n\n"
        "**Команды:**\n"
        "/start — Главное меню\n"
        "/help — Эта справка\n"
        "/skip — Пропустить поле при редактировании\n\n"
        "🆓 Бесплатно и без лимитов!",
        parse_mode="Markdown"
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main"))
    
    await callback.message.delete()

@router.callback_query(F.data == "back_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    """Вернуться в главное меню"""
    await callback.message.edit_text(
        "🎵 **Файл загружен. Что будем делать?**",
        parse_mode="Markdown",
        reply_markup=main_menu_kb()
    )

def register_tags_handlers(dp):
    dp.include_router(router)