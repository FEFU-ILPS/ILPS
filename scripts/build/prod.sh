#!/bin/bash

ROOT_DIR="$PWD"

source "${ROOT_DIR}/scripts/build/utils/nginx.sh"
source "${ROOT_DIR}/scripts/build/utils/certs.sh"

if [ -z "$1" ]; then
  echo "❌ Ошибка: Не указан домен"
  echo "Использование:"
  echo ""
  echo "  ./prod.sh <домен>"
  echo ""
  echo "Пример:"
  echo "  ./prod.sh ilps-example.ru"
  exit 1
fi

DOMAIN="$1"


if [ ! -f "${ROOT_DIR}/.env" ] || [ ! -f "${ROOT_DIR}/init.sql" ]; then
  echo "❌ Ошибка: Отсутствуют необходимые файлы .env или init.sql"
  echo "Пожалуйста, выполните:"
  echo ""
  echo "  ./scripts/configure.sh"
  echo ""
  exit 1
fi

export PROJECT_ROOT="$ROOT_DIR"


generate_nginx_config "$DOMAIN" "http"


docker-compose -f ./build/docker-compose.yml up -d

if [ $? -eq 0 ]; then
  echo "✅ Развертывание ILPS в среде PROD успешно завершено."
else
  echo "❌ Ошибка при развертывании ILPS в среде PROD."
  exit 1
fi

echo "🚀 Запуск процесса получения SSL-сертификатов"
obtain_certificates_for_domain "$DOMAIN" "nginx-letsencrypt"

generate_nginx_config "$DOMAIN" "https"

echo "🔄 Перезапуск Nginx..."
docker exec -it "nginx-letsencrypt" nginx -s reload