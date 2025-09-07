# Imagem base
FROM python:3.11-slim

# Diretório de trabalho
WORKDIR /app

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

# Expor porta (opcional, para teste)
EXPOSE 8000

# Usar o entrypoint que espera o Postgres antes de rodar Django
ENTRYPOINT ["/entrypoint.sh"]