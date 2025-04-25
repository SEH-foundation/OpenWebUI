#!/bin/bash
set -e

# запуск бэкенда
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
