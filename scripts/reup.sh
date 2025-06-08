#!/usr/bin/env bash

# -*- coding: utf-8 -*-
#
# Скрипт пересборки docker-compose сервиса

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$PWD"
COMPOSE_DIR="$PROJECT_ROOT/build"

# ----------------------------
# Вспомогательные функции
# ----------------------------

function die() {
    echo -e "\n${RED}Ошибка: ${1}${NC}" >&2
    exit 1
}

function select_environment() {
    echo -e "\n${BLUE}Выберите окружение:${NC}"
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

function select_service() {
    local compose_file="$1"
    
    echo -e "\n${BLUE}Доступные сервисы:${NC}"
    local services=($(docker-compose -f "$compose_file" config --services))
    
    for i in "${!services[@]}"; do
        echo "$((i+1))) ${services[$i]}"
    done
    
    while true; do
        read -p "Выберите сервис для пересборки [1-${#services[@]}]: " choice
        
        if [[ "$choice" =~ ^[0-9]+$ && "$choice" -ge 1 && "$choice" -le ${#services[@]} ]]; then
            SELECTED_SERVICE="${services[$((choice-1))]}"
            break
        else
            echo -e "${YELLOW}Неверный выбор. Пожалуйста, введите число от 1 до ${#services[@]}.${NC}"
        fi
    done
}

function confirm_action() {
    local message="$1"
    
    while true; do
        read -p "${message} [y/N]: " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            return 0
        elif [[ $REPLY =~ ^[Nn]$ || -z "$REPLY" ]]; then
            return 1
        fi
    done
}

# ----------------------------
# Главная функция
# ----------------------------

function main() {
    echo -e "\n${GREEN}=== Пересборка docker-compose сервиса ===${NC}"
    
    select_environment
    
    local compose_file="$COMPOSE_DIR/docker-compose.${ENV_TYPE}.yml"
    
    export PROJECT_ROOT

    if [[ ! -f "$compose_file" ]]; then
        die "Файл docker-compose ${compose_file} не найден"
    fi

    select_service "$compose_file"

    echo -e "\n${BLUE}Параметры пересборки:${NC}"
    echo -e "Окружение: ${GREEN}${ENV_TYPE}${NC}"
    echo -e "Сервис: ${GREEN}${SELECTED_SERVICE}${NC}"
    echo -e "Режим: ${GREEN}Без кеша${NC}"
    
    if confirm_action "Начать пересборку сервиса ${SELECTED_SERVICE}?"; then
        echo -e "\n${BLUE}Пересборка сервиса ${SELECTED_SERVICE}...${NC}"
        
        # Пересборка без кеша с принудительным обновлением зависимостей
        docker-compose -f "$compose_file" build --no-cache "${SELECTED_SERVICE}" && \
        docker-compose -f "$compose_file" up -d --no-deps "${SELECTED_SERVICE}"
        
        echo -e "\n${GREEN}Сервис ${SELECTED_SERVICE} успешно пересобран!${NC}"
    else
        echo -e "${YELLOW}Пересборка отменена${NC}"
    fi
}

# Запуск главной функции
main "$@"