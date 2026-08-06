FROM python:3.13-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


RUN curl -sSL https://install.python-poetry.org | python3
ENV PATH="/root/.local/bin:$PATH"


COPY pyproject.toml poetry.lock* ./


RUN --mount=type=cache,target=/root/.cache/pypoetry \
    poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main --no-root

FROM python:3.13-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

COPY --from=builder /usr/local/lib/python3.13/site-packages \
               /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin


COPY . .

RUN useradd --create-home appuser
USER appuser

EXPOSE 8001


CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8001"]