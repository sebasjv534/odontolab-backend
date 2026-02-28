#!/usr/bin/env bash
# Build script for Render
# Script de inicio para FastAPI en Azure App Service

# El puerto lo asigna Azure automáticamente (no tocar esta línea)
PORT=${PORT:-8000}

echo "=========================================="
echo "🚀 Iniciando FastAPI en el puerto $PORT"
echo "📁 Archivo principal: app/main.py"
echo "🔧 Instancia de FastAPI: app"
echo "=========================================="

# Iniciar con Gunicorn + Uvicorn
# -w 4 = 4 workers (procesos)
# -k uvicorn.workers.UvicornWorker = usar Uvicorn como worker
# app.main:app = archivo app/main.py, instancia app
# --bind 0.0.0.0:$PORT = escuchar en todas las interfaces en el puerto asignado

gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT
