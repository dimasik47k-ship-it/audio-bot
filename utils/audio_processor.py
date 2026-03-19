import os
from pathlib import Path
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, APIC, ID3NoHeaderError
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover
from utils.ffmpeg_runner import run_ffmpeg

SUPPORTED_FORMATS = {'.mp3', '.flac', '.m4a', '.aac', '.ogg', '.wav', '.wma', '.opus'}

def get_audio_info(filepath: str) -> dict:
    """Получить информацию о файле и тегах"""
    try:
        audio = MutagenFile(filepath)
    except Exception as e:
        return {"error": str(e), "duration": 0, "tags": {}}
    
    if not audio:
        return {"error": "Не распознан формат", "duration": 0, "tags": {}}
    
    info = {
        "format": type(audio).__name__,
        "duration": getattr(audio.info, 'length', 0),
        "bitrate": getattr(audio.info, 'bitrate', 0),
        "tags": {},
        "has_cover": False
    }
    
    if audio.tags:
        if isinstance(audio, ID3):
            info["tags"]["title"] = str(audio.get('TIT2', ''))
            info["tags"]["artist"] = str(audio.get('TPE1', ''))
            info["tags"]["album"] = str(audio.get('TALB', ''))
            info["tags"]["date"] = str(audio.get('TDRC', ''))
            info["tags"]["genre"] = str(audio.get('TCON', ''))
            info["has_cover"] = bool(audio.get('APIC:'))
        else:
            for key, value in audio.tags.items():
                info["tags"][key] = str(value)[:100]
    
    return info

def edit_tags(filepath: str, tags: dict, cover_path: str = None) -> str:
    """Редактировать теги и добавить обложку"""
    ext = Path(filepath).suffix.lower()
    
    try:
        if ext == '.mp3':
            try:
                audio = ID3(filepath)
            except ID3NoHeaderError:
                audio = ID3()
                audio.save(filepath)
                audio = ID3(filepath)
            
            # Удаляем старую обложку
            if 'APIC:' in audio:
                del audio['APIC:']
            
            if tags.get('title'):
                audio['TIT2'] = TIT2(encoding=3, text=tags['title'][:30])
            if tags.get('artist'):
                audio['TPE1'] = TPE1(encoding=3, text=tags['artist'][:30])
            if tags.get('album'):
                audio['TALB'] = TALB(encoding=3, text=tags['album'][:30])
            if tags.get('date'):
                audio['TDRC'] = TDRC(encoding=3, text=tags['date'][:4])
            if tags.get('genre'):
                audio['TCON'] = TCON(encoding=3, text=tags['genre'][:30])
            
            if cover_path and os.path.exists(cover_path):
                with open(cover_path, 'rb') as img:
                    img_data = img.read()
                
                mime_type = 'image/jpeg'
                if cover_path.lower().endswith('.png'):
                    mime_type = 'image/png'
                
                audio.add(APIC(
                    encoding=3,
                    mime=mime_type,
                    type=3,
                    desc='Cover',
                    data=img_data
                ))
            
            audio.save(v2_version=3)
            
        elif ext == '.flac':
            audio = FLAC(filepath)
            audio.clear_pictures()
            
            if tags.get('title'):
                audio['title'] = tags['title'][:30]
            if tags.get('artist'):
                audio['artist'] = tags['artist'][:30]
            if tags.get('album'):
                audio['album'] = tags['album'][:30]
            if tags.get('date'):
                audio['date'] = tags['date'][:4]
            if tags.get('genre'):
                audio['genre'] = tags['genre'][:30]
            
            if cover_path and os.path.exists(cover_path):
                pic = Picture()
                pic.type = 3
                pic.mime = 'image/jpeg'
                with open(cover_path, 'rb') as img:
                    pic.data = img.read()
                audio.add_picture(pic)
            
            audio.save()
            
        elif ext in ['.m4a', '.aac']:
            audio = MP4(filepath)
            
            if tags.get('title'):
                audio['\xa9nam'] = tags['title'][:30]
            if tags.get('artist'):
                audio['\xa9ART'] = tags['artist'][:30]
            if tags.get('album'):
                audio['\xa9alb'] = tags['album'][:30]
            if tags.get('date'):
                audio['\xa9day'] = tags['date'][:4]
            if tags.get('genre'):
                audio['\xa9gen'] = tags['genre'][:30]
            
            if cover_path and os.path.exists(cover_path):
                with open(cover_path, 'rb') as img:
                    img_data = img.read()
                
                if cover_path.lower().endswith('.png'):
                    try:
                        from PIL import Image
                        img_obj = Image.open(cover_path)
                        img_obj = img_obj.convert('RGB')
                        jpg_path = cover_path.replace('.png', '.jpg')
                        img_obj.save(jpg_path, 'JPEG')
                        with open(jpg_path, 'rb') as jpg:
                            img_data = jpg.read()
                    except:
                        pass
                
                audio['covr'] = [MP4Cover(img_data, imageformat=MP4Cover.FORMAT_JPEG)]
            
            audio.save()
            
        else:
            audio = MutagenFile(filepath, easy=True)
            if audio and audio.tags:
                if tags.get('title'):
                    audio['title'] = tags['title'][:30]
                if tags.get('artist'):
                    audio['artist'] = tags['artist'][:30]
                if tags.get('album'):
                    audio['album'] = tags['album'][:30]
                audio.save()
    
    except Exception as e:
        print(f"Ошибка тегов: {e}")
        raise RuntimeError("Ошибка записи тегов")
    
    return filepath

async def convert_format(input_path: str, output_format: str, bitrate: str = None) -> str:
    """Конвертировать файл через ffmpeg"""
    output_path = Path(input_path).with_suffix(f'.{output_format}')
    
    cmd = ['ffmpeg', '-i', input_path, '-y']
    
    if output_format == 'mp3':
        cmd.extend([
            '-codec:a', 'libmp3lame',
            '-b:a', bitrate or '192k',
            '-ar', '44100',
            '-ac', '2'
        ])
    elif output_format == 'flac':
        cmd.extend(['-compression_level', '8'])
    elif output_format == 'ogg':
        cmd.extend(['-codec:a', 'libvorbis', '-q:a', '6'])
    elif output_format == 'm4a':
        cmd.extend(['-codec:a', 'aac', '-b:a', '256k', '-ar', '44100'])
    
    cmd.append(str(output_path))
    
    await run_ffmpeg(cmd)
    
    return str(output_path)

def clear_all_tags(filepath: str) -> str:
    """Удалить все теги из файла"""
    ext = Path(filepath).suffix.lower()
    
    try:
        if ext == '.mp3':
            try:
                audio = ID3(filepath)
                audio.delete()
            except ID3NoHeaderError:
                pass
        elif ext == '.flac':
            audio = FLAC(filepath)
            audio.clear_pictures()
            if audio.tags:
                audio.delete()
            audio.save()
        elif ext in ['.m4a', '.aac']:
            audio = MP4(filepath)
            audio.delete()
            audio.save()
        else:
            audio = MutagenFile(filepath)
            if audio and audio.tags:
                audio.delete()
                audio.save()
    except Exception as e:
        print(f"Ошибка очистки: {e}")
        raise RuntimeError("Ошибка очистки тегов")
    
    return filepath