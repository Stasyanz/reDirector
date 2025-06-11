import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# ID группы для пересылки
TARGET_GROUP_ID = os.getenv("TARGET_GROUP_ID")
if not TARGET_GROUP_ID:
    raise ValueError("TARGET_GROUP_ID не установлен в переменных окружения")

try:
    TARGET_GROUP_ID = int(TARGET_GROUP_ID)
except ValueError:
    raise ValueError("TARGET_GROUP_ID должен быть числом")

# Username канала (без @)
SOURCE_CHANNEL_USERNAME = os.getenv("SOURCE_CHANNEL_USERNAME")
if not SOURCE_CHANNEL_USERNAME:
    raise ValueError("SOURCE_CHANNEL_USERNAME не установлен в переменных окружения")

# Убираем @ если он есть
if SOURCE_CHANNEL_USERNAME.startswith("@"):
    SOURCE_CHANNEL_USERNAME = SOURCE_CHANNEL_USERNAME[1:]

# ID топика в группе (опционально)
MESSAGE_THREAD_ID = os.getenv("MESSAGE_THREAD_ID")
if MESSAGE_THREAD_ID:
    try:
        MESSAGE_THREAD_ID = int(MESSAGE_THREAD_ID)
    except ValueError:
        raise ValueError("MESSAGE_THREAD_ID должен быть числом")

# ID администратора (опционально)
ADMIN_ID = os.getenv("ADMIN_ID")
if ADMIN_ID:
    try:
        ADMIN_ID = int(ADMIN_ID)
    except ValueError:
        raise ValueError("ADMIN_ID должен быть числом") 