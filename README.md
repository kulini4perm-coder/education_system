## Запуск проекта через Docker (Развертывание)

Для запуска всей системы приложения (Django, PostgreSQL, Redis, Celery, Celery Beat) единой командой выполните:

1. Настройте файл конфигурации `.env` на основе шаблона `.env_sample`.
2. Запустите сборку и старт контейнеров:
   ```bash
   docker-compose up --build
   ```
3. Для выполнения миграций базы данных внутри запущенного контейнера откройте новый терминал и введите:
   ```bash
   docker-compose exec web python manage.py migrate
   ```
4. Для создания суперпользователя:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```
