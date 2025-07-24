#!/bin/bash
echo "Начинаю деплой"
# Загружаем переменные из .env.test
set -o allexport
source .env.test
set +o allexport
echo "Проверяю .env.test"
# Проверяем переменные
if [[ -z "$DEPLOY_USER" || -z "$DEPLOY_PASS" || -z "$DEPLOY_HOST" || -z "$DEPLOY_PATH" ]]; then
  echo "❌ Не все переменные заданы в .env.test"
  exit 1
fi

# Отправка через SCP с паролем
echo "Отправка dist на сервер..."
sshpass -p "$DEPLOY_PASS" scp -r dist "${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}" || {
  echo "!! SCP не удался"; exit 1;
}

echo "Деплой завершён успешно"