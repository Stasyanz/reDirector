import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ContentType
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from config import BOT_TOKEN, TARGET_GROUP_ID, ADMIN_ID, SOURCE_CHANNEL_USERNAME, MESSAGE_THREAD_ID

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def start_command(message: Message):
    """Обработчик команды /start"""
    if message.from_user and message.from_user.id == ADMIN_ID:
        await message.answer(
            "🤖 Бот запущен!\n\n"
            f"📺 Отслеживаемый канал: @{SOURCE_CHANNEL_USERNAME}\n"
            f"🎯 Целевая группа: {TARGET_GROUP_ID}\n\n"
            "Добавьте меня в канал как администратора с правами:\n"
            "• Просмотр сообщений\n"
            "• Отправка сообщений\n\n"
            "Бот будет автоматически пересылать все сообщения из указанного канала в целевую группу."
        )
    else:
        await message.answer("Этот бот предназначен для пересылки сообщений из канала в группу.")


@dp.message(Command("status"))
async def status_command(message: Message):
    """Показать статус бота"""
    if message.from_user and message.from_user.id == ADMIN_ID:
        try:
            # Проверяем доступ к целевой группе
            chat_info = await bot.get_chat(TARGET_GROUP_ID)
            await message.answer(
                f"✅ Статус бота:\n"
                f"📺 Отслеживаемый канал: @{SOURCE_CHANNEL_USERNAME}\n"
                f"🎯 Целевая группа: {chat_info.title}\n"
                f"🆔 ID группы: {TARGET_GROUP_ID}\n"
                f"📊 Бот работает нормально"
            )
        except Exception as e:
            await message.answer(f"❌ Ошибка доступа к группе: {e}")


@dp.channel_post()
async def forward_channel_post(message: Message):
    """Пересылка сообщений из канала в группу"""
    try:
        # Логируем информацию о полученном посте
        logger.info(f"📥 Получен пост из канала: {message.chat.title} (@{message.chat.username})")
        
        # Проверяем, что это нужный канал
        if not message.chat.username:
            logger.warning(f"❌ Канал без username: {message.chat.title} (ID: {message.chat.id})")
            return
            
        if message.chat.username.lower() != SOURCE_CHANNEL_USERNAME.lower():
            logger.info(f"ℹ️ Пост из другого канала: @{message.chat.username} (ожидается @{SOURCE_CHANNEL_USERNAME})")
            return
        
        # Пересылаем сообщение в целевую группу
        forward_params = {
            "chat_id": TARGET_GROUP_ID,
            "from_chat_id": message.chat.id,
            "message_id": message.message_id
        }
        
        # Добавляем топик, если указан
        if MESSAGE_THREAD_ID:
            forward_params["message_thread_id"] = MESSAGE_THREAD_ID
            
        forwarded = await bot.forward_message(**forward_params)
        
        topic_info = f" в топик {MESSAGE_THREAD_ID}" if MESSAGE_THREAD_ID else ""
        logger.info(f"Сообщение успешно переслано в группу {TARGET_GROUP_ID}{topic_info}")
        
    except TelegramBadRequest as e:
        logger.error(f"Ошибка при пересылке сообщения: {e}")
        if "chat not found" in str(e).lower():
            logger.error("Группа не найдена. Проверьте TARGET_GROUP_ID")
        elif "not enough rights" in str(e).lower():
            logger.error("Недостаточно прав для пересылки в группу")
    
    except TelegramForbiddenError as e:
        logger.error(f"Доступ запрещен: {e}")
        logger.error("Бот должен быть добавлен в группу как администратор")
    
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")


@dp.edited_channel_post()
async def forward_edited_channel_post(message: Message):
    """Пересылка отредактированных сообщений из канала"""
    logger.info("Получено отредактированное сообщение из канала - пропускаем")
    # Можно также пересылать отредактированные сообщения, если нужно
    # await forward_channel_post(message)


@dp.message()
async def handle_regular_messages(message: Message):
    """Обработчик обычных сообщений (не из канала)"""
    logger.debug(f"Получено обычное сообщение от {message.from_user.username if message.from_user else 'Unknown'}")
    # Этот обработчик нужен для команд в личке и группах


async def main():
    """Главная функция запуска бота"""
    logger.info("Запуск бота...")
    
    try:
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"Бот @{bot_info.username} успешно запущен")
        
        # Проверяем доступ к целевой группе
        try:
            chat_info = await bot.get_chat(TARGET_GROUP_ID)
            logger.info(f"Целевая группа: {chat_info.title} (ID: {TARGET_GROUP_ID})")
        except Exception as e:
            logger.warning(f"Не удалось получить информацию о целевой группе: {e}")
        
        # Проверяем доступ к исходному каналу
        try:
            source_chat = await bot.get_chat(f"@{SOURCE_CHANNEL_USERNAME}")
            logger.info(f"Отслеживаемый канал: @{SOURCE_CHANNEL_USERNAME} ({source_chat.title})")
        except Exception as e:
            logger.warning(f"Не удалось получить информацию об отслеживаемом канале: {e}")
        
        # Запускаем polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main()) 