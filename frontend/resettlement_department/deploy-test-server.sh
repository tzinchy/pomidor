#!/usr/bin/env bash
set -euo pipefail

echo "📦 Проверка зависимостей..."

for cmd in sshpass scp; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "❌ Требуется '$cmd', но он не найден."
        echo "👉 Установи Git Bash + sshpass. Подсказка:"
        echo "   choco install sshpass"  # если есть Chocolatey
        exit 1
    fi
done

echo "🚀 Начинаю деплой..."

# Загружаем переменные из .env.production
set -o allexport
source .env.test
set +o allexport

echo "📄 Проверяю .env.test..."

if [[ -z "${DEPLOY_USER:-}" || -z "${DEPLOY_PASS:-}" || -z "${DEPLOY_HOST:-}" || -z "${DEPLOY_PATH:-}" ]]; then
  echo "❌ Не все переменные заданы в .env.test"
  exit 1
fi

echo "📤 Отправка dist на сервер $DEPLOY_HOST..."
sshpass -p "$DEPLOY_PASS" scp -r dist "${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}" || {
  echo "❌ SCP не удался"
  exit 1
}

echo "✅ Деплой завершён успешно"