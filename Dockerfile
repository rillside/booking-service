# --- Этап 1: Сборка dependencies ---
FROM python:3.11-slim AS builder

WORKDIR /app

# МЕНЯЕМ НА ВЕРСИЮ 2.0+
ENV POETRY_VERSION=2.0.1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

RUN pip install "poetry==$POETRY_VERSION"

# Копируем файлы конфигурации
COPY pyproject.toml poetry.lock ./

# В Poetry 2.0+ для установки продакшн-зависимостей используется флаг --without dev
RUN poetry install --without dev

# --- Этап 2: Финальный образ ---
FROM python:3.11-slim AS runtime

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
