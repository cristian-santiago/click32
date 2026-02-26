#!/bin/sh

echo "Esperando o Postgres ficar pronto..."
while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" > /dev/null 2>&1; do
    sleep 1
done

echo "Banco pronto! Aplicando migrations..."
python manage.py migrate --noinput

echo "Coletando e comprimindo arquivos estáticos..."
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# A versão já vem do .env via settings
echo "STATIC_VERSION=$STATIC_VERSION"t

chown -R www-data:www-data /app/staticfiles

echo "Iniciando Gunicorn..."
exec gunicorn --workers 3 --bind 0.0.0.0:8000 click32.wsgi:application