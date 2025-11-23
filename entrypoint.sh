#!/bin/sh

echo "Esperando o Postgres ficar pronto..."

while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" > /dev/null 2>&1; do
    sleep 1
done

echo "Banco pronto! Aplicando migrations..."

python manage.py migrate --noinput
# To load dev data, uncomment the line below
#python manage.py loaddata db.json

echo "Coletando e comprimindo arquivos estáticos..."

python manage.py collectstatic --noinput

# Comprimir apenas se for produção
if [ "$COMPRESS_ENABLED" = "True" ]; then
    echo "Comprimindo arquivos CSS/JS..."
    python manage.py compress --verbosity=0
fi

chown -R www-data:www-data /app/staticfiles

echo "Iniciando Gunicorn..."
exec gunicorn --workers 3 --bind 0.0.0.0:8000 click32.wsgi:application