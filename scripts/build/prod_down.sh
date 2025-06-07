#!/bin/bash
set -euo pipefail

# === Настройки ===
readonly ROOT_DIR="$PWD"
readonly COMPOSE_FILE="${ROOT_DIR}/build/docker-compose.yml"

# === Основной процесс ===
main() {
  echo "🛑 Остановка PROD-среды..."

  if [ ! -f "$COMPOSE_FILE" ]; then
    echo "❌ Файл $COMPOSE_FILE не найден." >&2
    exit 1
  fi

  echo "🐳 Выполнение 'docker-compose -f $COMPOSE_FILE down'..."
  docker-compose -f "$COMPOSE_FILE" down --volumes --remove-orphans

  if [ $? -eq 0 ]; then
    echo "✅ PROD-среда успешно остановлена и очищена."
  else
    echo "❌ Ошибка при остановке PROD-среды." >&2
    exit 1
  fi
}

main "$@"