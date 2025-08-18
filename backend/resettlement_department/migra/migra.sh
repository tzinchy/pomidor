#!/usr/bin/env bash
# set -euo pipefail
export PYTHONWARNINGS="ignore::UserWarning"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../.venv/bin/activate"
ENV_FILE="$SCRIPT_DIR/.env"

#Загружаем .env
if [ -f "$ENV_FILE" ]; then
  echo "Загружаем переменные из $ENV_FILE"
  set -a
  source "$ENV_FILE"
  set +a
else
  echo ".env не найден рядом со скриптом ($ENV_FILE)"
  exit 1
fi

: "${SOURCE_DATABASE_URL:?Укажите SOURCE_DATABASE_URL}"
: "${TARGET_DATABASE_URL:?Укажите TARGET_DATABASE_URL}"

#Сравниваем схемы
echo "ℹ Сравнение схем: source → target"
MIGRA_CMD="migra \"$SOURCE_DATABASE_URL\" \"$TARGET_DATABASE_URL\" --unsafe"

eval $MIGRA_CMD
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
  echo "   [WARNING] MIGRA завершилась с кодом $EXIT_CODE"
  echo "   Был применен флаг --unsafe"
  echo "   Подумайте хорошенько"
fi

#Подтверждение
echo -n "Применить изменения? (yes/no): "
read confirm
if [[ "$confirm" != "yes" ]]; then
  echo "Отменено"
  exit 0
fi
#Применяем diff через psql
eval "$MIGRA_CMD" | psql "$SOURCE_DATABASE_URL"
echo "Схема целевой БД обновлена под новую"