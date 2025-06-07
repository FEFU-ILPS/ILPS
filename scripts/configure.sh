#!/bin/bash

ROOT_DIR="$PWD"
EXAMPLES_DIR="${ROOT_DIR}/examples"

if [ ! -d "$EXAMPLES_DIR" ]; then
  echo "❌ Папка examples не найдена по пути: $EXAMPLES_DIR"
  exit 1
fi

cd "$EXAMPLES_DIR" || exit 1

if [ -f ".env.example" ]; then
  cp ".env.example" "$ROOT_DIR/.env"
  echo "✅ .env создан в корне проекта"
else
  echo "⚠️ .env.example не найден в папке examples"
fi

if [ -f "init.sql.example" ]; then
  cp "init.sql.example" "$ROOT_DIR/init.sql"
  echo "✅ init.sql создан в корне проекта"
else
  echo "⚠️ init.sql.example не найден в папке examples"
fi