#!/bin/bash
set -e

# A verificação de espera foi REMOVIDA daqui.
# O Docker Compose já garante que o postgres está pronto.

echo "📊 Executando migrações do Django..."
python manage.py migrate --noinput

echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear || true

echo "🚀 Iniciando aplicação..."
exec "$@"