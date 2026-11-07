# Imagem da API Antimicrobiano Inteligente (execução reprodutível).
# Construir:  docker build -t antimicrobiano-inteligente .
# Executar:   docker compose up   (ver docker-compose.yml)

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Usuário sem privilégios e pasta de dados persistida em volume (RNF02, RNF05).
RUN useradd --create-home --uid 10001 ami \
    && mkdir -p /dados \
    && chown ami:ami /dados

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install .

USER ami

ENV AMI_DATABASE_URL=sqlite:////dados/antimicrobiano.db \
    AMI_ARQUIVO_ENV=

EXPOSE 8000
VOLUME ["/dados"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4)"

CMD ["uvicorn", "antimicrobiano.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
