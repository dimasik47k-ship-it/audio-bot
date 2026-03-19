import asyncio
import subprocess
import sys
from pathlib import Path
from config import FFMPEG_PATH

async def run_ffmpeg(cmd: list):
    """Запустить ffmpeg"""
    # На Render ffmpeg уже установлен в системе
    if sys.platform != "win32" or not FFMPEG_PATH.exists():
        cmd[0] = 'ffmpeg'  # Используем системный ffmpeg
    else:
        cmd[0] = str(FFMPEG_PATH)
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {stderr.decode('utf-8', errors='ignore')[:500]}")
    
    return stdout