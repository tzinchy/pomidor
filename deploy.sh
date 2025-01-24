#!/bin/bash

# Определяем путь к директории, в которой находится сам скрипт
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Переходим в рабочую директорию
cd "$SCRIPT_DIR"

# Выполняем обновление репозитория и перезапуск сервиса
git pull origin main
sudo systemctl restart resettlement_backend
#sudo systemctl restart resettlement_frontend
