#!/bin/sh
set -e  # para parar se houver erro

echo "Esperando o Postgres ficar pronto..."
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done

echo "Banco pronto! Aplicando migrations..."
python manage.py makemigrations
python manage.py migrate

exec "$@"  # executa o comando passado no docker-compose
