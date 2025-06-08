#!/usr/bin/env bash

# -*- coding: utf-8 -*-
#
# Скрипт генерации конфигурации Nginx из шаблонов

set -euo pipefail

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ----------------------------
# Вспомогательные функции
# ----------------------------

function die() {
    echo -e "${RED}Ошибка: ${1}${NC}" >&2
    exit 1
}

function require_file() {
    local file_path="$1"
    local error_msg="${2:-Файл не найден}"
    
    if [[ ! -f "$file_path" ]]; then
        die "${error_msg} — ${file_path}"
        return 1
    fi
}

function generate_config_from_template() {
    local template_path="$1"
    local output_path="$2"
    export domain="$3"

    envsubst '$domain' < "$template_path" > "$output_path" || {
        die "Не удалось сгенерировать конфиг из шаблона ${template_path}"
    }
}

# ----------------------------
# Основная функция
# ----------------------------

function generate_nginx_config() {
    local domain="$1"
    local proto="$2"

    if [[ "$proto" != "http" && "$proto" != "https" ]]; then
        die "Неверный протокол — допустимо только 'http' или 'https'"
    fi

    # Настройка путей
    export PROJECT_ROOT="${PROJECT_ROOT:-$PWD}"
    local nginx_sites_enabled="${PROJECT_ROOT}/nginx/sites-enabled"
    local template_dir="${PROJECT_ROOT}/templates/nginx/${proto}"

    mkdir -p "$nginx_sites_enabled" || die "Не удалось создать директорию ${nginx_sites_enabled}"

    # Список шаблонов
    declare -A templates=(
        ["ilps.conf.template"]="${domain}.conf"
        ["admin.ilps.conf.template"]="admin.${domain}.conf"
    )

    # Обработка шаблонов
    echo -e "\n${BLUE}Генерация конфигурации Nginx для ${domain} (${proto})...${NC}"
    
    for template_file in "${!templates[@]}"; do
        local output_file="${templates[$template_file]}"
        local template_path="${template_dir}/${template_file}"
        local output_path="${nginx_sites_enabled}/${output_file}"

        require_file "$template_path" "Шаблон Nginx не найден" || return 1

        echo -e "  Создание ${output_file} из шаблона"
        generate_config_from_template "$template_path" "$output_path" "$domain"
    done

    echo -e "\n${GREEN}Конфигурация Nginx успешно создана${NC}"
}

# ----------------------------
# Главная функция
# ----------------------------

function main() {
    if [[ $# -ne 2 ]]; then
        echo -e "\n${RED}Необходимо указать домен и протокол${NC}"
        echo -e "${BLUE}Пример:${NC} $0 example.com https"
        exit 1
    fi

    generate_nginx_config "$1" "$2"
}

# Запуск главной функции
main "$@"