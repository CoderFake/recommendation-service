#!/bin/bash

echo "Starting application in PRODUCTION environment..."
docker compose -f docker-compose.yml -f prod.yml up -d

echo "Showing logs (Ctrl+C to exit logs, service will continue running)..."
docker compose -f docker-compose.yml -f prod.yml logs -f api