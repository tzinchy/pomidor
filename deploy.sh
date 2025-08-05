#!/bin/bash

# Определяем путь к директории, в которой находится сам скрипт
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Получаем IP-адрес текущей машины (первый внешний)
ip=$(hostname -I | awk '{print $1}')
MAIN_IPS=("10.9.96.160")
branch="dev"

# Переходим в рабочую директорию
cd "$SCRIPT_DIR"

# Проверка: если IP найден в MAIN_IPS — переключаемся на main
for main_ip in "${MAIN_IPS[@]}"; do
  if [[ "$ip" == "$main_ip" ]]; then
    branch="main"
    break
  fi
done

# Убедимся, что нужная ветка активна
git checkout "$branch" || exit 1

# Выполняем обновление репозитория и перезапуск сервиса
git pull upstream "$branch"

sudo systemctl restart resettlement_backend
sudo chown -R dsa-dgi:dsa-dgi /opt/auth
sudo chmod -R 777 /opt/auth
cp -r backend/auth_service/app /opt/auth/
sudo chown -R dsa-dgi:dsa-dgi /opt/auth
sudo chmod -R 777 /opt/auth
sudo systemctl restart auth
#sudo systemctl restart resettlement_frontend
