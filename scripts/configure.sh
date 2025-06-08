#!/usr/bin/env bash

# -*- coding: utf-8 -*-
#
# Мастер конфигурации переменных среды
#
# Автоматически генерирует конфигурационные файлы из шаблонов
# с подстановкой значений, введённых пользователем

# Цвета для вывода в консоль
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

typeset -A CONFIG_VARS=()

PROJECT_ROOT="$PWD"

# ----------------------------
# Вспомогательные функции
# ----------------------------


# Функция для вывода сообщения об ошибке и завершения скрипта
function die() {
    echo -e "\n${RED}Ошибка: ${1}${NC}" >&2
    exit 1
}


# Функция для проверки наличия необходимых команд
function check_dependencies() {
    local dependencies=("envsubst" "find")
    
    for cmd in "${dependencies[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            die "Необходимая команда '$cmd' не найдена. Убедитесь, что она установлена."
        fi
    done
}


# Функция для поиска .template файлов
function find_template_files() {
    local templates_dir="$1"
    
    echo -e "\n${BLUE}Поиск файлов шаблонов в ${templates_dir}...${NC}"
    
    local template_files=()
    while IFS= read -r -d $'\0' file; do
        template_files+=("$file")
    done < <(find "$templates_dir" -maxdepth 1 -type f -name "*.template" -print0)
    
    if [[ ${#template_files[@]} -eq 0 ]]; then
        echo -e "\n${YELLOW}Предупреждение: Не найдено ни одного .template файла в указанной директории.${NC}"
        return 1
    fi
    
    echo -e "Найдены следующие файлы шаблонов:"
    for file in "${template_files[@]}"; do
        echo -e "  - ${GREEN}${file}${NC}"
    done
    
    TEMPLATE_FILES=("${template_files[@]}")
}


# Функция для генерации HEX паролей
function generate_hex_password() {
    local length="$1"
    head /dev/urandom | tr -dc 'a-f0-9' | fold -w "$length" | head -n1
}

# ----------------------------
# Основные функции
# ----------------------------


# Функция для выбора типа окружения
function select_environment() {
    echo -e "\n${BLUE}Выберите тип окружения:${NC}"
    echo -e "1) Production (Производственная среда)"
    echo -e "2) Development (Разработка)"
    
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

# Функция для конфигурации администратора по умолчанию
function configure_admin() {
    echo -e "\n${YELLOW}Настройка администратора по умолчанию${NC}"
    
    while true; do
        read -p "Логин администратора: " ADMIN_LOGIN
        if [[ -z "$ADMIN_LOGIN" ]]; then
            echo -e "${RED}Логин не может быть пустым!${NC}"
            continue
        fi
        break
    done
    
    while true; do
        read -s -p "Пароль администратора: " ADMIN_PASSWORD
        echo
        if [[ -z "$ADMIN_PASSWORD" ]]; then
            echo -e "${RED}Пароль не может быть пустым!${NC}"
            continue
        fi
        read -s -p "Подтвердите пароль: " ADMIN_PASSWORD_CONFIRM
        echo
        if [[ "$ADMIN_PASSWORD" != "$ADMIN_PASSWORD_CONFIRM" ]]; then
            echo -e "${RED}Пароли не совпадают!${NC}"
            continue
        fi
        break
    done
    
    while true; do
        read -p "Email администратора: " ADMIN_EMAIL
        if [[ ! "$ADMIN_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
            echo -e "${RED}Некорректный email!${NC}"
            continue
        fi
        break
    done

    CONFIG_VARS["ADMIN_LOGIN"]="$ADMIN_LOGIN"
    CONFIG_VARS["ADMIN_PASSWORD"]="$ADMIN_PASSWORD"
    CONFIG_VARS["ADMIN_EMAIL"]="$ADMIN_EMAIL"
}


# Функция для нейронных моделий распознования произношения
function configure_ai_models() {
    echo -e "\n${YELLOW}Настройка нейронных моделей${NC}"
    
    local predefined_languages=("English")
    local default_drive_link="https://drive.google.com/drive/folders/..."
    
    for lang in "${predefined_languages[@]}"; do
        local var_name="MODEL_$(echo "$lang" | tr '[:lower:]' '[:upper:]' | tr ' ' '_')"
        local link_var_name="${var_name}_LINK"
        
        read -p "Ссылка на папку Google Drive для ${lang} (Enter для пропуска): " drive_link
        drive_link=${drive_link:-$default_drive_link}
        
        CONFIG_VARS["$var_name"]="$lang"
        CONFIG_VARS["$link_var_name"]="$drive_link"
        
        if [[ ! "$drive_link" =~ ^https?:// ]]; then
            echo -e "${YELLOW}Предупреждение: Ссылка может быть не валидной.${NC}"
        fi
    done
}


# Функция для конфигурации окружения разработки
function configure_development() {
    echo -e "\n${BLUE}Настройка Development окружения${NC}"
    
    read -p "Включить режим отладки (True/False) [по умолчанию True]: " DEBUG_MODE
    DEBUG_MODE=${DEBUG_MODE:-True}

    local DEV_PASSWORD="password123"  

    CONFIG_VARS["DEBUG_MODE"]="$DEBUG_MODE"

    CONFIG_VARS["PG_PASSWORD"]="$DEV_PASSWORD"
    CONFIG_VARS["AUTH_JWT_SECRET"]="$DEV_PASSWORD"
    CONFIG_VARS["AUTH_DB_PASSWORD"]="$DEV_PASSWORD"
    CONFIG_VARS["TEXTS_DB_PASSWORD"]="$DEV_PASSWORD"
    CONFIG_VARS["EXERCISES_DB_PASSWORD"]="$DEV_PASSWORD"
    CONFIG_VARS["MANAGER_DB_PASSWORD"]="$DEV_PASSWORD"

    CONFIG_VARS["ADMIN_LOGIN"]="admin"
    CONFIG_VARS["ADMIN_PASSWORD"]="$DEV_PASSWORD"
    CONFIG_VARS["ADMIN_EMAIL"]="admin@ilpsadmin.com"

    configure_ai_models
}


# Функция для конфигурации продуктового окружения
function configure_production() {
    echo -e "\n${BLUE}Настройка Production окружения${NC}"
    
    read -p "Длина HEX паролей [по умолчанию 32]: " PASSWORD_LENGTH
    PASSWORD_LENGTH=${PASSWORD_LENGTH:-32}
    
    echo -e "\n${YELLOW}Генерация секретных ключей...${NC}"

    CONFIG_VARS["DEBUG_MODE"]="False"

    CONFIG_VARS["PG_PASSWORD"]=$(generate_hex_password "$PASSWORD_LENGTH")
    
    CONFIG_VARS["AUTH_JWT_SECRET"]=$(generate_hex_password "$PASSWORD_LENGTH")
    CONFIG_VARS["AUTH_DB_PASSWORD"]=$(generate_hex_password "$PASSWORD_LENGTH")

    CONFIG_VARS["TEXTS_DB_PASSWORD"]=$(generate_hex_password "$PASSWORD_LENGTH")
    CONFIG_VARS["EXERCISES_DB_PASSWORD"]=$(generate_hex_password "$PASSWORD_LENGTH")
    CONFIG_VARS["MANAGER_DB_PASSWORD"]=$(generate_hex_password "$PASSWORD_LENGTH")

    echo -e "\n${GREEN}Секретные ключи успешно сгенерированы${NC}"

    configure_admin

    configure_ai_models
}


# Функция генерации конфигурационных файлов
function generate_configs() {
    local output_dir="$1"

    echo -e "\n${BLUE}Генерация конфигурационных файлов...${NC}"
    
    # Экспортируем все переменные для envsubst
    echo "$CONFIG_VARS"

    for key in "${!CONFIG_VARS[@]}"; do
        export "$key"="${CONFIG_VARS[$key]}"
    done
    
    for template_file in "${TEMPLATE_FILES[@]}"; do
        local base=${template_file##*/}
        local output_file="${base%.template}"
        
        echo -e "  Генерация ${YELLOW}${output_file}${NC} из шаблона"
        
        envsubst < "$template_file" > "$output_dir/$output_file" || die "Ошибка при генерации файла ${output_file}"
        
        echo -e "  ${GREEN}Успешно создан: ${output_file}${NC}\n"
    done
}


# ----------------------------
# Главный код
# ----------------------------


function main() {
    check_dependencies

    find_template_files "${PROJECT_ROOT}/templates"
    
    echo -e "\n${GREEN}=== Мастер конфигурации переменных среды ===${NC}"


    if [[ -n "${1:-}" ]]; then
        ENV_TYPE="$1"
        case "$ENV_TYPE" in
            production|development)
                echo -e "\n${BLUE}Выбрано окружение: ${ENV_TYPE}${NC}"
                ;;
            *)
                die "Ошибка: Неизвестный тип окружения '${ENV_TYPE}'."
                ;;
        esac
    else
        select_environment
    fi
    
    case "$ENV_TYPE" in
        production)
            configure_production
            ;;
        development)
            configure_development
            ;;
        *)
            die "Неизвестный тип окружения"
            ;;
    esac

    echo $CONFIG_VARS

    generate_configs "${PROJECT_ROOT}"
    
    echo -e "\n${GREEN}Конфигурация успешно завершена!${NC}"
}

main "$@"