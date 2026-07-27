FROM python:3.14-rc-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем настройки Python и версию Poetry
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=2.0.1 \
    POETRY_VIRTUALENVS_CREATE=false

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем менеджер пакетов Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Отключаем пакетный режим
RUN poetry config package-mode false

# Копируем файл зависимостей в контейнер
COPY pyproject.toml poetry.lock* ./

# Устанавливаем зависимости Python через Poetry
RUN poetry install --no-root --no-interaction --no-ansi

# Копируем исходный код приложения в контейнер
COPY . .

# Создаем директорию для медиафайлов (как в уроке)
RUN mkdir -p /app/media

# Пробрасываем порт, который будет использовать Django
EXPOSE 8000

# Команда для запуска приложения через сервер Gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]


