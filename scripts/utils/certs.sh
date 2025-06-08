#!/usr/bin/env bash

# -*- coding: utf-8 -*-
#
# Скрипт для получения SSL-сертификатов с помощью certbot контейнера

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

function obtain_ssl_certificate() {
    local container_name="$1"
    shift
    local -a domains=("$@")

    if [[ "${#domains[@]}" -eq 0 ]]; then
        echo -e "\n${YELLOW}Предупреждение: Нет доменов для получения сертификата${NC}"
        return 1
    fi

    echo -e "\n${BLUE}Получение SSL-сертификата для доменов: ${domains[*]}${NC}"
    
    docker exec -it "$container_name" certbot certonly \
        --webroot -w /usr/share/nginx/html \
        $(printf -- "--domain %s " "${domains[@]}") || {
        die "Не удалось получить сертификат для доменов: ${domains[*]}"
    }

    echo -e "\n${GREEN}Сертификат успешно получен для доменов: ${domains[*]}${NC}"
}

function generate_domain_groups() {
    local main_domain="$1"
    declare -A domain_groups=(
        ["main"]="$main_domain www.$main_domain"
        ["admin"]="admin.$main_domain www.admin.$main_domain"
    )

    for group in "${!domain_groups[@]}"; do
        echo "$group:${domain_groups[$group]}"
    done
}

# ----------------------------
# Основная функция
# ----------------------------

function obtain_certificates_for_domain() {
    local main_domain="$1"
    local container_name="${2:-nginx-letsencrypt}"

    echo -e "\n${GREEN}=== Получение SSL-сертификатов для домена: ${main_domain} ===${NC}"

    while IFS=":" read -r group domains; do
        local domain_list=($domains)

        echo -e "\n${BLUE}Обработка группы [${group}]: ${domain_list[*]}${NC}"
        obtain_ssl_certificate "$container_name" "${domain_list[@]}" || {
            die "Ошибка при получении сертификата для группы [${group}]"
        }
    done < <(generate_domain_groups "$main_domain")

    echo -e "\n${GREEN}Все SSL-сертификаты успешно получены для домена: ${main_domain}${NC}"
}

# ----------------------------
# Главная функция
# ----------------------------

function main() {
    if [[ $# -eq 0 ]]; then
        die "Необходимо указать основной домен в качестве аргумента"
    fi

    local main_domain="$1"
    local container_name="${2:-"nginx-letsencrypt"}"

    obtain_certificates_for_domain "$main_domain" "$container_name"
}

# Запуск главной функции
main "$@"