#!/bin/bash
# Переход в директорию скрипта
cd "$(dirname "$0")"

# Активируем виртуальное окружение
source .venv/bin/activate

cd "$(dirname "$0")/app"

# Запускаем приложение
uvicorn main:app --port 3123 --reload
