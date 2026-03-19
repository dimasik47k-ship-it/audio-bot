from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ Редактировать теги", callback_data="edit_tags"),
        InlineKeyboardButton(text="🔄 Конвертировать", callback_data="convert")
    )
    builder.row(
        InlineKeyboardButton(text="🎨 Добавить обложку", callback_data="add_cover"),
        InlineKeyboardButton(text="🗑️ Очистить теги", callback_data="clear_tags")
    )
    builder.row(
        InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")
    )
    return builder.as_markup()

def format_select_kb():
    builder = InlineKeyboardBuilder()
    formats = [
        ("MP3 320kbps", "fmt_mp3_320"),
        ("MP3 192kbps", "fmt_mp3_192"),
        ("FLAC (lossless)", "fmt_flac"),
        ("WAV", "fmt_wav"),
        ("M4A/AAC", "fmt_m4a"),
        ("OGG", "fmt_ogg")
    ]
    for text, cb in formats:
        builder.button(text=text, callback_data=cb)
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")
    )
    return builder.as_markup()

def help_text():
    return """
🎧 **AudioTool Bot — Помощь**

**Возможности:**
• ✏️ Редактирование тегов (название, артист, альбом, год, жанр)
• 🎨 Добавление обложки в аудиофайл
• 🔄 Конвертация между форматами (MP3, FLAC, WAV, M4A, OGG)
• 🗑️ Очистка всех тегов

**Поддерживаемые форматы:**
MP3, FLAC, M4A, AAC, WAV, OGG, OPUS, WMA

**Лимиты:**
• До 50 МБ на файл (стандартный лимит Telegram)
• Файлы удаляются через 1 час

**Команды:**
/start — Главное меню
/skip — Пропустить поле при редактировании

🆓 Бесплатно и без лимитов!
"""