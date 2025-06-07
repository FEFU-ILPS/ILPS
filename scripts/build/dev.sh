#!/bin/bash

ROOT_DIR="$PWD"

if [ ! -f "${ROOT_DIR}/.env" ] || [ ! -f "${ROOT_DIR}/init.sql" ]; then
  echo "❌ Ошибка: Отсутствуют необходимые файлы .env или init.sql"
  echo "Пожалуйста, выполните:"
  echo ""
  echo "  ./scripts/configure.sh"
  echo ""
  exit 1
fi

export PROJECT_ROOT="$ROOT_DIR"

docker-compose -f ./build/dev.docker-compose.yml up -d

if [ $? -eq 0 ]; then
  echo "✅ Развертывание ILPS в среде DEV успешно завершено."
else
  echo "❌ Ошибка при развертывании ILPS в среде DEV."
  exit 1
fi