
import os
from pathlib import Path

# Базовые пути
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

# Пути к файлам данных
ROLES_FILE = DATA_DIR / "roles.json"
PERMISSIONS_LEVELS_FILE = DATA_DIR / "permissions_levels.json"
TICKET_CATEGORIES_FILE = DATA_DIR / "ticket_categories.json"
TICKET_COUNT_FILE = DATA_DIR / "ticket_count.txt"

# Настройки бота
BOT_PREFIX = "/"
BOT_INTENTS = {
    "message_content": True,
    "guilds": True,
    "members": True
}

# Настройки тикетов
TICKET_FORM = [
    "Ваш никнейм в игре",
    "Подробное описание вашей проблемы (Опишите ситуацию / проблему детально)",
    "Если этого требует ситуация, предоставьте док-ва, которые будут отражать суть проблемы (Подойдут как скриншоты, так и видео)"
]

# Настройки embed-ов
EMBED_COLORS = {
    "default": 0xFFFFFF,
    "success": 0x00ff00,
    "error": 0xff0000,
    "warning": 0xffa500,
    "info": 0x0099ff
}

# Настройки UI
UI_TIMEOUTS = {
    "default": 60,
    "permanent": None
}

# Настройки прав доступа
PERMISSION_LEVELS = {
    "helper": 1,
    "senior_helper": 5,
    "junior_moderator": 10,
    "moderator": 15,
    "senior_moderator": 20,
    "junior_admin": 25,
    "admin": 30,
    "senior_admin": 35,
    "chief_admin": 40,
    "curator": 45,
    "chief_curator": 50
}

# Минимальные уровни для функций
MIN_PERMISSION_LEVELS = {
    "manage_ticket": 1,  # helper
    "assign_ticket": 35,  # senior_admin
    "close_ticket": 1,   # helper
    "send_transcript": 1  # helper
}
