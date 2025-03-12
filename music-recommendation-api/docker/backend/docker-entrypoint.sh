#!/bin/bash
set -e

if [ -z "$APP_ENV" ]; then
    echo "APP_ENV is not set, defaulting to 'dev'"
    export APP_ENV=dev
fi

echo "Running in $APP_ENV environment"
echo "Loading configuration from .env.$APP_ENV"

echo "Running database migrations..."
alembic upgrade head

exec "$@"