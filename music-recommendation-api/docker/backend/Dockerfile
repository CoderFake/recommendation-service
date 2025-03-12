FROM python:3.10-slim

WORKDIR /app/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN addgroup --system app && adduser --system --group app \
    && chown -R app:app /app

USER app

CMD ["bash", "-c", "\
    if [ -z \"$APP_ENV\" ]; then \
        echo \"APP_ENV is not set, defaulting to 'dev'\"; \
        export APP_ENV=dev; \
    fi; \
    echo \"Running in $APP_ENV environment\"; \
    echo \"Loading configuration from .env.$APP_ENV\"; \
    echo \"Running database migrations...\"; \
    alembic upgrade head; \
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 \
"]