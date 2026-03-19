from .file_handler import register_file_handlers
from .tags_handler import register_tags_handlers  
from .convert_handler import register_convert_handlers

def register_handlers(dp):
    register_file_handlers(dp)
    register_tags_handlers(dp)
    register_convert_handlers(dp)