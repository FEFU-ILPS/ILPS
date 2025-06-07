#!/bin/bash
set -euo pipefail

# === Настройки ===
readonly ROOT_DIR="$PWD"
readonly EXAMPLES_DIR="${ROOT_DIR}/examples"
readonly REQUIRED_EXAMPLE_FILES=(
  ".env.example"
  "init.sql.example"
)

# === Проверки ===
if [ ! -d "$EXAMPLES_DIR" ]; then
  echo "❌ Ошибка: Папка examples не найдена по пути: $EXAMPLES_DIR" >&2
  exit 1
fi

# === Функция копирования файла ===
copy_example_file() {
  local filename="$1"
  local src_path="${EXAMPLES_DIR}/${filename}"
  local dest_path="${ROOT_DIR}/${filename%.example}"

  if [ ! -f "$src_path" ]; then
    echo "⚠️ Файл $filename не найден в папке examples" >&2
    return 1
  fi

  cp "$src_path" "$dest_path"
  echo "✅ $filename скопирован как ${filename%.example}"
}

# === Основной процесс ===
main () {
  cd "$EXAMPLES_DIR"

  echo "⚙️ Конфигурация проекта..."

  for file in "${REQUIRED_EXAMPLE_FILES[@]}"; do
    copy_example_file "$file"
  done

  echo "🎉 Конфигурация завершена!"
}

# === Точка входа ===
main "$@"