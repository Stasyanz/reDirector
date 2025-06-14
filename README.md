# Telegram Redirect Bot

Телеграм бот для автоматической пересылки сообщений из канала в группу.

## Функциональность

- ✅ Автоматическая пересылка всех сообщений из определенного канала в указанную группу
- ✅ Поддержка всех типов сообщений (текст, фото, видео, документы и т.д.)
- ✅ Пересылка в конкретный топик (тему) группы
- ✅ Команды для управления и проверки статуса
- ✅ Детальное логирование работы
- ✅ Обработка ошибок

## Установка и настройка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# Токен бота от @BotFather
BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# Username канала для отслеживания (без @)
SOURCE_CHANNEL_USERNAME=your_channel_username

# ID группы, куда нужно пересылать сообщения (начинается с -100)
TARGET_GROUP_ID=-1001234567890

# ID топика в группе (опционально, для групп с включенными Topics)
MESSAGE_THREAD_ID=12345

# ID администратора бота (ваш Telegram ID)
ADMIN_ID=123456789
```

### 3. Получение необходимых данных

#### Токен бота:
1. Напишите @BotFather в Telegram
2. Создайте нового бота командой `/newbot`
3. Скопируйте полученный токен

#### Username канала:
1. Откройте настройки канала в Telegram
2. Скопируйте публичную ссылку канала (например: t.me/my_channel)
3. Используйте только username без @ (например: my_channel)

#### ID группы:
1. Добавьте бота @userinfobot в вашу группу
2. Отправьте любое сообщение в группу
3. Бот покажет ID группы (число, начинающееся с -100)
4. Удалите @userinfobot из группы

#### ID топика (опционально):
1. Откройте группу с включенными Topics
2. Зайдите в нужную тему
3. Посмотрите на URL: в нем будет `?thread=12345`
4. Число после `thread=` - это и есть MESSAGE_THREAD_ID

**Альтернативный способ:**
1. Включите режим разработчика в Telegram Desktop
2. Правый клик на сообщении в топике → "Копировать ссылку на сообщение"
3. В ссылке найдите параметр thread (например: `?thread=12345`)

#### Ваш ID:
1. Напишите @userinfobot в личные сообщения
2. Отправьте любое сообщение
3. Скопируйте ваш ID

## Запуск

### Локальный запуск

```bash
python bot.py
```

### Запуск с Docker

**Преимущества Docker:**
- ✅ Изолированная среда выполнения
- ✅ Автоматический перезапуск при сбоях
- ✅ Минимальное потребление ресурсов (32-64MB RAM)
- ✅ Простое развертывание на сервере
- ✅ Мониторинг здоровья контейнера

#### Быстрый запуск:
```bash
# Убедитесь, что .env файл настроен
docker-compose up -d
```

#### Управление контейнером:
```bash
# Запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Пересборка после изменения кода
docker-compose up --build -d

# Просмотр статуса
docker-compose ps
```

#### Использование Makefile (опционально):
```bash
# Показать все доступные команды
make help

# Запустить бота
make up

# Посмотреть логи  
make logs

# Остановить бота
make down

# Пересобрать и запустить
make rebuild
```

## Настройка в Telegram

### 1. Добавление в канал
1. Добавьте бота в канал как администратора
2. Дайте права:
   - ✅ Просмотр сообщений
   - ✅ Отправка сообщений

### 2. Добавление в группу
1. Добавьте бота в целевую группу
2. Дайте права администратора для пересылки сообщений

## Команды

- `/start` - Приветствие и инструкции
- `/status` - Проверка статуса работы бота

## Логирование

Бот ведет подробные логи:
- Информация о полученных сообщениях
- Успешные пересылки
- Ошибки и их описание

## Возможные ошибки

### "BOT_TOKEN не установлен в переменных окружения"
- Проверьте наличие файла `.env`
- Убедитесь, что токен указан правильно

### "SOURCE_CHANNEL_USERNAME не установлен в переменных окружения"
- Добавьте username канала в файл `.env`
- Используйте только имя канала без символа @

### "chat not found"
- Проверьте правильность ID группы
- Убедитесь, что бот добавлен в группу

### "not enough rights"
- Дайте боту права администратора в группе
- Проверьте права на пересылку сообщений

### "Доступ запрещен"
- Убедитесь, что бот добавлен в канал как администратор
- Проверьте права на просмотр сообщений

### "Сообщения из канала не поступают"
- Убедитесь, что бот добавлен в канал как **администратор**
- Проверьте права бота: "Просмотр сообщений" должно быть включено
- Убедитесь, что SOURCE_CHANNEL_USERNAME указан правильно (без @)
- Проверьте логи бота - там должны появляться сообщения "📥 Получен пост из канала"

### "MESSAGE_THREAD_ID должен быть числом"
- Проверьте правильность ID топика в файле `.env`
- ID топика должен быть числом (например: 12345)

### "Topic not found" или ошибки с топиками
- Убедитесь, что в группе включены Topics (Темы)
- Проверьте правильность MESSAGE_THREAD_ID
- Убедитесь, что топик существует и не был удален

## Структура проекта

```
redirect_bot/
├── bot.py              # Основной файл бота
├── config.py           # Конфигурация и загрузка переменных
├── requirements.txt    # Зависимости Python
├── Dockerfile          # Docker образ
├── docker-compose.yml  # Docker Compose конфигурация
├── Makefile            # Удобные команды для Docker
├── .dockerignore       # Исключения для Docker
├── .env               # Переменные окружения (создать самостоятельно)
├── .gitignore         # Исключения для Git
└── README.md          # Документация
``` 