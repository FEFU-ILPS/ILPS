#!/bin/bash

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

# Проверяет, существует ли файл, и выводит ошибку, если нет
require_file() {
  local file_path="$1"
  local error_msg="$2"

  if [ ! -f "$file_path" ]; then
    echo "❌ Ошибка: $error_msg — файл не найден: $file_path"
    return 1
  fi
}

# Генерирует конфиг на основе шаблона
generate_config_from_template() {
  local template_path="$1"
  local output_path="$2"
  export domain="$3"

  envsubst '$domain' < "$template_path" > "$output_path"
}

# === ОСНОВНАЯ ФУНКЦИЯ ===

generate_nginx_config() {
  # --- Проверка аргументов ---
  if [ -z "${1:-}" ] || [ -z "${2:-}" ]; then
    echo "❌ Ошибка: Требуются два аргумента"
    echo "Использование:"
    echo "  generate_nginx_config <домен> <протокол>"
    echo ""
    echo "Пример:"
    echo "  generate_nginx_config ilps-example.ru http"
    echo "  generate_nginx_config ilps-trainer.ru https"
    return 1
  fi

  local DOMAIN="$1"
  local PROTO="$2"

  # --- Проверка протокола ---
  if [[ "$PROTO" != "http" && "$PROTO" != "https" ]]; then
    echo "❌ Ошибка: Неверный протокол — допустимо только 'http' или 'https'"
    return 1
  fi

  # --- Настройка путей ---
  export PROJECT_ROOT="${PROJECT_ROOT:-$PWD}"

  local NGINX_SITES_ENABLED="${PROJECT_ROOT}/nginx/sites-enabled"
  local TEMPLATE_DIR="${PROJECT_ROOT}/examples/nginx/${PROTO}"

  mkdir -p "$NGINX_SITES_ENABLED"

  # --- Список шаблонов и соответствующих им выходных файлов ---
  local -a templates=(
    "ilps.conf.template=${DOMAIN}.conf"
    "admin.ilps.conf.template=admin.${DOMAIN}.conf"
  )

  # --- Обработка каждого шаблона ---
  for entry in "${templates[@]}"; do
    IFS="=" read -r template_file output_file <<< "$entry"

    local TEMPLATE_PATH="${TEMPLATE_DIR}/${template_file}"
    local OUTPUT_PATH="${NGINX_SITES_ENABLED}/${output_file}"

    # Проверяем наличие шаблона
    require_file "$TEMPLATE_PATH" "Шаблон Nginx не найден" || return 1

    # Генерируем конфиг
    generate_config_from_template "$TEMPLATE_PATH" "$OUTPUT_PATH" "$DOMAIN" || {
      echo "❌ Ошибка: Не удалось сгенерировать конфиг из $TEMPLATE_PATH"
      return 1
    }
  done

  echo "✅ Конфигурация Nginx для $PROTO создана."
}