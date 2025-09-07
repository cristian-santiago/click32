#!/bin/sh

echo "Esperando o Postgres ficar pronto..."

while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" > /dev/null 2>&1; do
            sleep 1
    done

    echo "Banco pronto! Aplicando migrations..."

    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver 0.0.0.0:8000

exec "$@"  # executa o comando passado no docker-compose