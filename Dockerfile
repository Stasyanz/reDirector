# Используем минимальный Python образ
FROM python:3.11-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем пользователя для безопасности
RUN addgroup -g 1001 -S botuser && \
    adduser -S botuser -u 1001 -G botuser

# Меняем владельца файлов
RUN chown -R botuser:botuser /app
USER botuser

# Запускаем бота
CMD ["python", "bot.py"] 