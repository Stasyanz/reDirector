import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ContentType, Update
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
            "Бот будет автоматически пересылать все сообщения из указанного канала в целевую группу.\n\n"
            "Команды:\n"
            "/status - статус бота\n"
            "/info - информация о чатах\n"
            "/test - тест отправки"
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


@dp.message(Command("info"))
async def info_command(message: Message):
    """Получить информацию о чатах (канал/группа)"""
    if message.from_user and message.from_user.id == ADMIN_ID:
        info_text = "🔍 **Информация о чатах:**\n\n"
        
        # Информация о целевой группе
        try:
            target_chat = await bot.get_chat(TARGET_GROUP_ID)
            info_text += f"🎯 **Целевая группа/канал:**\n"
            info_text += f"   • Название: {target_chat.title}\n"
            info_text += f"   • Тип: `{target_chat.type}`\n"
            info_text += f"   • ID: `{target_chat.id}`\n"
            info_text += f"   • Username: @{target_chat.username or 'Нет'}\n"
            
            # Проверяем топики
            if hasattr(target_chat, 'is_forum') and target_chat.is_forum:
                info_text += f"   • 📝 Форум с топиками: ДА\n"
            else:
                info_text += f"   • 📝 Форум с топиками: НЕТ\n"
            
            if MESSAGE_THREAD_ID:
                info_text += f"   • 🧵 ID топика: {MESSAGE_THREAD_ID}\n"
            
        except Exception as e:
            info_text += f"❌ Ошибка получения информации о целевой группе: {e}\n"
        
        info_text += "\n"
        
        # Информация об исходном канале
        try:
            source_chat = await bot.get_chat(f"@{SOURCE_CHANNEL_USERNAME}")
            info_text += f"📺 **Исходный чат:**\n"
            info_text += f"   • Название: {source_chat.title}\n"
            info_text += f"   • Тип: `{source_chat.type}`\n"
            info_text += f"   • ID: `{source_chat.id}`\n"
            info_text += f"   • Username: @{source_chat.username or 'Нет'}\n"
            
            if hasattr(source_chat, 'is_forum') and source_chat.is_forum:
                info_text += f"   • 📝 Форум с топиками: ДА\n"
            else:
                info_text += f"   • 📝 Форум с топиками: НЕТ\n"
                
        except Exception as e:
            info_text += f"❌ Ошибка получения информации об исходном чате: {e}\n"
        
        await message.answer(info_text, parse_mode="Markdown")


@dp.message(Command("test"))
async def test_command(message: Message):
    """Тестовая команда для проверки пересылки"""
    if message.from_user and message.from_user.id == ADMIN_ID:
        try:
            # Отправляем тестовое сообщение в целевую группу
            test_params = {
                "chat_id": TARGET_GROUP_ID,
                "text": "🧪 Тестовое сообщение от бота для проверки работы пересылки"
            }
            
            if MESSAGE_THREAD_ID:
                test_params["message_thread_id"] = MESSAGE_THREAD_ID
                
            sent = await bot.send_message(**test_params)
            await message.answer(f"✅ Тестовое сообщение отправлено (ID: {sent.message_id})")
        except Exception as e:
            await message.answer(f"❌ Ошибка при отправке тестового сообщения: {e}")


async def forward_message_logic(message: Message, source_type: str):
    """Общая логика пересылки сообщений"""
    try:
        # Детальное логирование сообщения
        logger.info(f"🔍 [{source_type}] Получено сообщение:")
        logger.info(f"  - Чат: {message.chat.title} (@{message.chat.username}) ID: {message.chat.id}")
        logger.info(f"  - Тип чата: {message.chat.type}")
        logger.info(f"  - Контент: {message.content_type}")
        
        # Проверяем топик
        if hasattr(message, 'message_thread_id') and message.message_thread_id:
            logger.info(f"  - Топик ID: {message.message_thread_id}")
        
        if message.document:
            logger.info(f"  - Документ: {message.document.file_name} ({message.document.file_size} bytes)")
            logger.info(f"  - MIME: {message.document.mime_type}")
        
        if message.text:
            logger.info(f"  - Текст: {message.text[:100]}...")
            
        # Проверяем, что это нужный канал
        if not message.chat.username:
            logger.warning(f"❌ Чат без username: {message.chat.title} (ID: {message.chat.id})")
            return
            
        if message.chat.username.lower() != SOURCE_CHANNEL_USERNAME.lower():
            logger.info(f"ℹ️ Сообщение из другого чата: @{message.chat.username} (ожидается @{SOURCE_CHANNEL_USERNAME})")
            return
        
        logger.info(f"✅ Чат совпадает! Пересылаем сообщение...")
        
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
        logger.info(f"✅ Сообщение успешно переслано в группу {TARGET_GROUP_ID}{topic_info}")
        logger.info(f"   ID пересланного сообщения: {forwarded.message_id}")
        
    except TelegramBadRequest as e:
        logger.error(f"❌ Ошибка при пересылке сообщения: {e}")
        if "chat not found" in str(e).lower():
            logger.error("💡 Группа не найдена. Проверьте TARGET_GROUP_ID")
        elif "not enough rights" in str(e).lower():
            logger.error("💡 Недостаточно прав для пересылки в группу")
        elif "message to forward not found" in str(e).lower():
            logger.error("💡 Исходное сообщение не найдено")
    
    except TelegramForbiddenError as e:
        logger.error(f"❌ Доступ запрещен: {e}")
        logger.error("💡 Бот должен быть добавлен в группу как администратор")
    
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")


@dp.channel_post()
async def forward_channel_post(message: Message):
    """Пересылка сообщений из канала в группу"""
    logger.info("📺 CHANNEL_POST обработчик сработал!")
    await forward_message_logic(message, "CHANNEL_POST")


@dp.edited_channel_post()
async def forward_edited_channel_post(message: Message):
    """Пересылка отредактированных сообщений из канала"""
    logger.info("📝 EDITED_CHANNEL_POST обработчик сработал!")
    # Можно также пересылать отредактированные сообщения, если нужно
    # await forward_message_logic(message, "EDITED_CHANNEL_POST")


@dp.message()
async def handle_regular_messages(message: Message):
    """Обработчик обычных сообщений (не из канала)"""
    # Проверяем, может ли это быть сообщение из группы/супергруппы
    if message.chat.type in ["group", "supergroup"]:
        logger.info("📨 ОБЫЧНОЕ сообщение из группы/супергруппы")
        await forward_message_logic(message, "REGULAR_MESSAGE_FROM_GROUP")
    elif message.chat.type == "channel":
        logger.info("📨 ОБЫЧНОЕ сообщение из канала (возможно, права не позволяют получать channel_post)")
        await forward_message_logic(message, "REGULAR_MESSAGE_FROM_CHANNEL")
    else:
        logger.debug(f"💬 Получено обычное сообщение от {message.from_user.username if message.from_user else 'Unknown'}")


# Добавляем middleware для логирования всех обновлений
@dp.update.outer_middleware()
async def log_all_updates(handler, event: Update, data):
    """Middleware для логирования всех типов обновлений"""
    logger.info(f"🔄 Получено обновление типа: {type(event).__name__}")
    
    if event.message:
        logger.info(f"   📄 Message: {event.message.chat.type} - {event.message.chat.title} (@{event.message.chat.username or 'Нет'})")
    elif event.channel_post:
        logger.info(f"   📺 Channel Post: {event.channel_post.chat.title} (@{event.channel_post.chat.username or 'Нет'})")
    elif event.edited_channel_post:
        logger.info(f"   📝 Edited Channel Post: {event.edited_channel_post.chat.title}")
    elif event.edited_message:
        logger.info(f"   ✏️ Edited Message: {event.edited_message.chat.title}")
    else:
        logger.info(f"   ❓ Другой тип обновления")
    
    return await handler(event, data)


async def main():
    """Главная функция запуска бота"""
    logger.info("🚀 Запуск бота...")
    
    try:
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"✅ Бот @{bot_info.username} успешно запущен")
        
        # Проверяем доступ к целевой группе
        try:
            chat_info = await bot.get_chat(TARGET_GROUP_ID)
            logger.info(f"🎯 Целевая группа: {chat_info.title} (ID: {TARGET_GROUP_ID})")
            logger.info(f"    Тип: {chat_info.type}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось получить информацию о целевой группе: {e}")
        
        # Проверяем доступ к исходному каналу
        try:
            source_chat = await bot.get_chat(f"@{SOURCE_CHANNEL_USERNAME}")
            logger.info(f"📺 Отслеживаемый чат: @{SOURCE_CHANNEL_USERNAME} ({source_chat.title})")
            logger.info(f"    Тип: {source_chat.type}")
            logger.info(f"    ID: {source_chat.id}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось получить информацию об отслеживаемом чате: {e}")
        
        # Запускаем polling
        logger.info("🔄 Запуск polling...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main()) 