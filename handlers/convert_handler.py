from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from utils.audio_processor import convert_format
from utils.ui import format_select_kb

router = Router()

@router.callback_query(F.data == "convert")
async def start_convert(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get('file_path'):
        await callback.answer("❌ Файл не найден", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🔄 **Выберите формат для конвертации:**",
        parse_mode="Markdown",
        reply_markup=format_select_kb()
    )

@router.callback_query(F.data.startswith("fmt_"))
async def process_convert(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    file_path = data.get('file_path')
    original_name = data.get('original_name', 'audio')
    
    if not file_path:
        await callback.answer("❌ Файл не найден", show_alert=True)
        return
    
    format_code = callback.data.replace("fmt_", "")
    
    format_map = {
        'mp3_320': ('mp3', '320k'),
        'mp3_192': ('mp3', '192k'),
        'flac': ('flac', None),
        'wav': ('wav', None),
        'm4a': ('m4a', None),
        'ogg': ('ogg', None)
    }
    
    if format_code not in format_map:
        await callback.answer("❌ Неверный формат", show_alert=True)
        return
    
    output_format, bitrate = format_map[format_code]
    
    status_msg = await callback.message.edit_text(
        f"⏳ Конвертирую в **{output_format.upper()}**..."
    )
    
    try:
        new_file = await convert_format(file_path, output_format, bitrate)
        
        audio = types.FSInputFile(new_file)
        
        # 🔧 Важно: отправляем как audio с правильным MIME type
        if output_format == 'mp3':
            await callback.message.bot.send_audio(
                chat_id=callback.message.chat.id,
                audio=audio,
                caption=f"✅ Конвертировано в **{output_format.upper()}**",
                parse_mode="Markdown"
            )
        else:
            # Для других форматов тоже пробуем send_audio
            await callback.message.bot.send_audio(
                chat_id=callback.message.chat.id,
                audio=audio,
                caption=f"✅ Конвертировано в **{output_format.upper()}**",
                parse_mode="Markdown"
            )
        
        await status_msg.delete()
        
    except Exception as e:
        await status_msg.edit_text(
            "❌ Ошибка конвертации. Попробуйте другой формат.",
            parse_mode=None
        )
    
    await state.clear()

@router.callback_query(F.data == "back_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🎵 **Что будем делать?**",
        parse_mode="Markdown",
        reply_markup=main_menu_kb()
    )

def register_convert_handlers(dp):
    dp.include_router(router)