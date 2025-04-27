#!/bin/bash
set -e

echo "Инициализация папок для данных..."

mkdir -p /data/uploads
mkdir -p /data/cache

echo "Папки готовы."

# Проверка что папка /data доступна
echo "Проверяю доступность /data..."
timeout=30
while [ ! -d "/data" ] && [ $timeout -gt 0 ]; do
    echo "Ожидание монтирования Volume... Осталось ${timeout} секунд"
    sleep 1
    timeout=$((timeout - 1))
done

if [ ! -d "/data" ]; then
    echo "Volume /data так и не смонтирован! Завершаем старт."
    exit 1
fi

echo "Volume /data доступен."

echo "Запуск OpenWebUI Backend на порту ${PORT:-8080}..."
exec uvicorn open_webui.main:app --host 0.0.0.0 --port ${PORT:-8080} --proxy-headers --forwarded-allow-ips="*"

