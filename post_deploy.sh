#!/usr/bin/env bash
# Post-deploy hook para Render
# Este script se ejecuta automáticamente después del despliegue

set -o errexit

echo "🚀 Running post-deploy tasks..."

# Inicializar la base de datos automáticamente
echo "📊 Initializing database..."
python init_db_render.py

echo "✅ Post-deploy tasks completed!"
