#!/bin/bash
set -euo pipefail

# === Настройки ===
readonly ROOT_DIR="$PWD"
readonly SCRIPTS_DIR="${ROOT_DIR}/scripts"

source "${SCRIPTS_DIR}/build/utils/nginx.sh"
source "${SCRIPTS_DIR}/build/utils/certs.sh"

# === Проверка аргумента домена ===
if [ -z "${1:-}" ]; then
  echo "❌ Ошибка: Не указан домен" >&2
  echo "Использование:" >&2
  echo "" >&2
  echo "  ./prod.sh <домен>" >&2
  echo "" >&2
  echo "Пример:" >&2
  echo "  ./prod.sh ilps-example.ru" >&2
  exit 1
fi

DOMAIN="$1"

# === Проверка наличия необходимых файлов ===
check_required_files() {
  local missing=false

  if [ ! -f "${ROOT_DIR}/.env" ]; then
    echo "❌ Ошибка: Файл .env не найден в корне проекта" >&2
    missing=true
  fi

  if [ ! -f "${ROOT_DIR}/init.sql" ]; then
    echo "❌ Ошибка: Файл init.sql не найден в корне проекта" >&2
    missing=true
  fi

  if [ "$missing" = true ]; then
    echo "Пожалуйста, выполните:" >&2
    echo "" >&2
    echo "  ./scripts/configure.sh" >&2
    echo "" >&2
    exit 1
  fi
}

# === Основной процесс ===
main() {
  echo "🚀 Запуск PROD-развертывания ILPS для домена: $DOMAIN"

  # Проверяем наличие файлов
  echo "🔍 Проверка наличия необходимых файлов..."
  check_required_files

  export PROJECT_ROOT="$ROOT_DIR"

  echo "📝 Генерация HTTP-конфига для Nginx..."
  generate_nginx_config "$DOMAIN" "http"

  echo "🐳 Запуск docker-compose.yml..."
  docker-compose -f "${ROOT_DIR}/build/docker-compose.yml" up -d

  if [ $? -ne 0 ]; then
    echo "❌ Ошибка при запуске контейнеров" >&2
    exit 1
  fi

  echo "🔐 Получение SSL-сертификатов..."
  obtain_certificates_for_domain "$DOMAIN" "nginx-letsencrypt"

  echo "📝 Генерация HTTPS-конфига для Nginx..."
  generate_nginx_config "$DOMAIN" "https"

  # Перезагрузка Nginx
  echo "🔄 Перезапуск Nginx..."
  docker exec -it "nginx-letsencrypt" nginx -s reload

  echo "🎉 PROD-развертывание успешно завершено!"
}

# === Точка входа ===
main "$@"