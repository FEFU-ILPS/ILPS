#!/usr/bin/env bash

# -*- coding: utf-8 -*-
#
# Скрипт остановки docker-compose с разными конфигурациями

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
    echo -e "\n${BLUE}Выберите тип окружения для остановки:${NC}"
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

function confirm_action() {
    local message="$1"
    local default="${2:-no}"
    
    while true; do
        if [[ "$default" == "yes" ]]; then
            prompt="${message} [Y/n] "
        else
            prompt="${message} [y/N] "
        fi
        
        read -p "$prompt" -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            return 0
        elif [[ $REPLY =~ ^[Nn]$ ]]; then
            return 1
        elif [[ -z "$REPLY" ]]; then
            [[ "$default" == "yes" ]] && return 0 || return 1
        fi
    done
}

# ----------------------------
# Главная функция
# ----------------------------

function main() {
    echo -e "\n${GREEN}=== Остановка ILPS сервисов ===${NC}"
    
    select_environment
    
    local compose_file="$COMPOSE_DIR/docker-compose.${ENV_TYPE}.yml"
    
    if [[ ! -f "$compose_file" ]]; then
        die "Файл docker-compose ${compose_file} не найден"
    fi

    # Выбор опций удаления
    local down_args=()
    
    if confirm_action "Удалить volumes (данные БД будут потеряны)?"; then
        down_args+=("--volumes")
        echo -e "${YELLOW}Будут удалены все volumes${NC}"
    fi
    
    if confirm_action "Удалить образы контейнеров?"; then
        down_args+=("--rmi" "all")
        echo -e "${YELLOW}Будут удалены все образы и кеш${NC}"
    fi

    # Подтверждение действия
    echo -e "\n${RED}Внимание! Будут остановлены все сервисы ${ENV_TYPE} окружения${NC}"
    if ! confirm_action "Продолжить?" "no"; then
        echo -e "${GREEN}Отмена операции${NC}"
        exit 0
    fi

    export PROJECT_ROOT

    # Выполнение команды
    echo -e "\n${BLUE}Остановка docker-compose...${NC}"
    docker-compose -f "$compose_file" down "${down_args[@]}"

    echo -e "\n${GREEN}Готово! Сервисы ${ENV_TYPE} окружения остановлены.${NC}"
    
    if [[ "${#down_args[@]}" -gt 0 ]]; then
        echo -e "${YELLOW}Дополнительные ресурсы были удалены${NC}"
    fi

    if confirm_action "Очистить кеш и временные файлы?"; then
        docker system prune -af
    fi
}

# Запуск главной функции
main "$@"