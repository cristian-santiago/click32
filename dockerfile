# Imagem base
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro para aproveitar cache do Docker
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o projeto
COPY . .

# Variáveis de ambiente para Django
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=click32.settings

# Expor porta (opcional, para teste)
EXPOSE 8000

# Entry point para criar migrations e aplicar no banco limpo
CMD ["sh", "-c", "\
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py runserver 0.0.0.0:8000"]