#!/bin/sh

echo "Esperando o Postgres ficar pronto..."

while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" > /dev/null 2>&1; do
    sleep 1
done

echo "Banco pronto! Aplicando migrations..."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "Iniciando Gunicorn..."
exec gunicorn --workers 3 --bind 0.0.0.0:8000 click32.wsgi:application