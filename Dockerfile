# Используем базовый образ Python
FROM python:3.10

# Устанавливаем переменные окружения для Django
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл requirements.txt и устанавливаем зависимости
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Копируем все остальные файлы проекта
COPY . /app/

# Выполняем миграции и собираем статику (при необходимости)
# RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Команда запуска Gunicorn
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "5"]
# CMD ["sh", "-c", "python manage.py migrate && gunicorn core.wsgi:application --bind 0.0.0.0:8000"]