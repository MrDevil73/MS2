# Укажите базовый образ (Python, например)
FROM python:3.9

# Установите рабочую директорию внутри контейнера
WORKDIR /app

# Скопируйте файлы проекта в контейнер
COPY . /app

# Установите зависимости проекта
RUN pip install -r requirements.txt

# Установите переменные среды для Django
EXPOSE 5432
# Выполните миграции базы данных
RUN python manage.py migrate

# Откройте порт, на котором будет работать Django
EXPOSE 8000

# Запустите сервер Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]