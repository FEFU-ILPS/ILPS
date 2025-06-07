#!/bin/bash

set -euo pipefail

# === Настройки ===
readonly ROOT_DIR="$PWD"
readonly ENV_FILE="${ROOT_DIR}/.env"
readonly INIT_SQL_FILE="${ROOT_DIR}/init.sql"
readonly COMPOSE_FILE="${ROOT_DIR}/build/dev.docker-compose.yml"

# === Проверка наличия необходимых файлов ===
ensure_required_files() {
  if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Ошибка: Файл .env не найден в корне проекта" >&2
    return 1
  fi

  if [ ! -f "$INIT_SQL_FILE" ]; then
    echo "❌ Ошибка: Файл init.sql не найден в корне проекта" >&2
    return 1
  fi
}

# === Основной процесс ===
main() {
  echo "⚙️ Начат процесс развёртывания ILPS в DEV среду..."

  # Проверяем наличие файлов
  echo "🔍 Проверка наличие необходимых файлов..."
  ensure_required_files || {
    echo "Пожалуйста, выполните:" >&2
    echo ""
    echo "  ./scripts/configure.sh" >&2
    echo ""
    exit 1
  }

  # Экспортируем переменную окружения
  export PROJECT_ROOT="$ROOT_DIR"

  # Запуск Docker Compose
  echo "🐳 Запуск dev.docker-compose.yml..."
  docker-compose -f "$COMPOSE_FILE" up -d

  if [ $? -eq 0 ]; then
    echo "✅ Развертывание ILPS в среде DEV успешно завершено."
  else
    echo "❌ Ошибка при развертывании ILPS в DEV среде." >&2
    exit 1
  fi
}

# === Точка входа ===
main "$@"