#!/usr/bin/env bash

# -*- coding: utf-8 -*-
#
# Скрипт запуска docker-compose с разными конфигурациями


# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$PWD"
COMPOSE_DIR="$PROJECT_ROOT/build"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

# ----------------------------
# Вспомогательные функции
# ----------------------------

function die() {
    echo -e "\n${RED}Ошибка: ${1}${NC}" >&2
    exit 1
}

function select_environment() {
    echo -e "\n${BLUE}Выберите тип окружения:${NC}"
    echo -e "1) Production (Продовое)"
    echo -e "2) Development (Разработочное)"
    
    while true; do
        read -p "Введите номер варианта [1-2]: " choice
        
        case $choice in
            1)
                ENV_TYPE="production"
                break
                ;;
            2)
                ENV_TYPE="development"
                break
                ;;
            *)
                echo -e "${YELLOW}Неверный выбор. Пожалуйста, введите 1 или 2.${NC}"
                ;;
        esac
    done
}

function check_config_files() {
    local missing_files=()
    
    if [[ ! -f ".env" ]]; then
        missing_files+=(".env")
    fi
    
    if [[ ! -f "init.sql" ]]; then
        missing_files+=("init.sql")
    fi
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        echo -e "\n${YELLOW}Отсутствуют необходимые файлы конфигурации: ${missing_files[*]}${NC}"
        return 1
    fi
    
    return 0
}

function reload_nginx() {
    echo -e "\n${BLUE}Перезагрузка Nginx...${NC}"

    docker-compose -f "$compose_file" exec nginx nginx -s reload || \
        echo -e "${YELLOW}Предупреждение: не удалось перезагрузить Nginx${NC}"
}

# ----------------------------
# Главная функция
# ----------------------------

function main() {
    echo -e "\n${GREEN}=== Мастер развёртывания ILPS ===${NC}"
    
    select_environment
    
    if ! check_config_files; then
        echo -e "\n${BLUE}Запуск скрипта configure.sh для генерации конфигурации...${NC}"
        "$SCRIPTS_DIR/configure.sh" "$ENV_TYPE" || die "Не удалось выполнить configure.sh"
    fi
    
    local compose_file="docker-compose.${ENV_TYPE}.yml"
    
    if [[ ! -f "$COMPOSE_DIR/$compose_file" ]]; then
        die "Файл docker-compose ${compose_file} не найден"
    fi
    
    export PROJECT_ROOT

    echo -e "\n${BLUE}Запуск docker-compose с конфигурацией ${ENV_TYPE}...${NC}"
    docker-compose -f "$COMPOSE_DIR/$compose_file" up -d
    
    echo -e "\n${GREEN}Готово! Сервисы запущены в ${ENV_TYPE} режиме.${NC}"
}

# Запуск главной функции
main "$@"