#!/bin/sh

echo "Esperando o Postgres ficar pronto..."

while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" > /dev/null 2>&1; do
    sleep 1
done

echo "Banco pronto! Aplicando migrations..."

python manage.py migrate --noinput
# To load dev data, uncomment the line below
#python manage.py loaddata db.json
python manage.py collectstatic --noinput
chown -R www-data:www-data /app/staticfiles

echo "Iniciando Gunicorn..."
exec gunicorn --workers 3 --bind 0.0.0.0:8000 click32.wsgi:application
