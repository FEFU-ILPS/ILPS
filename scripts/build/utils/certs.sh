#!/bin/bash

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

obtain_ssl_certificate() {
  local container_name="$1"
  shift
  local -a domains=("$@")

  if [ "${#domains[@]}" -eq 0 ]; then
    echo "⚠️ Нет доменов для получения сертификата"
    return 1
  fi

  echo "📝 Получение SSL-сертификат для доменов: ${domains[*]}"
  docker exec -it "$container_name" certbot certonly \
    --webroot -w /usr/share/nginx/html \
    $(printf -- "--domain %s " "${domains[@]}")

  if [ $? -ne 0 ]; then
    echo "❌ Ошибка: Не удалось получить сертификат для доменов: ${domains[*]}"
    return 1
  fi

  echo "✅ Сертификат успешно получен для доменов: ${domains[*]}"
}

generate_domain_groups() {
  local main_domain="$1"

  local -A domain_groups=(
    ["main"]="$main_domain www.$main_domain"
    ["admin"]="admin.$main_domain www.admin.$main_domain"
  )

  for group in "${!domain_groups[@]}"; do
    echo "$group:${domain_groups[$group]}"
  done
}

# === ОСНОВНАЯ ФУНКЦИЯ ===

obtain_certificates_for_domain() {
  local MAIN_DOMAIN="$1"
  local CONTAINER_NAME="${2:-nginx-letsencrypt}"

  echo "🔐 Получение SSL-сертификатов для домена: $MAIN_DOMAIN"

  while IFS=":" read -r group domains; do
    local domain_list=($domains)

    echo "🔄 Группа [$group]: ${domain_list[*]}"
    obtain_ssl_certificate "$CONTAINER_NAME" "${domain_list[@]}" || {
      echo "❌ Ошибка при получении сертификата для группы [$group]"
      return 1
    }
  done < <(generate_domain_groups "$MAIN_DOMAIN")

  echo "🎉 Все SSL-сертификаты успешно получены для домена: $MAIN_DOMAIN"
}