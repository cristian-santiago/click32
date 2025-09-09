# Imagem base
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

# Cria as pastas necessárias no build da imagem
RUN mkdir -p /app/media/stores /app/media/flyers \
    && chmod -R 755 /app/media

# Instala dependências do sistema necessárias para psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev gcc postgresql-client poppler-utils\
    && apt-get clean

# Copiar requirements primeiro para aproveitar cache do Docker
COPY requirements.txt .

# Atualizar pip e instalar dependências Python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar todo o projeto
COPY . .

# Copiar entrypoint e dar permissão de execução
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Variáveis de ambiente para Django
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=click32.settings

# Expor porta
EXPOSE 8000

# Usar o entrypoint
ENTRYPOINT ["/entrypoint.sh"]