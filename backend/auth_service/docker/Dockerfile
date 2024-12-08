FROM python:3.12

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Устанавливаем рабочую директорию на auth_service
WORKDIR /auth_service

# Копируем зависимости
COPY requirements.txt /auth_service/
RUN pip install -r requirements.txt

# Копируем весь проект в контейнер
COPY . /auth_service/

# Устанавливаем PYTHONPATH
ENV PYTHONPATH=/auth_service/app

# Открываем порт
EXPOSE 8000

# Указываем команду для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
