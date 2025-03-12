#!/bin/bash

echo "Starting application in DEVELOPMENT environment..."
docker compose -f docker-compose.yml -f dev.yml up -d

echo "Showing logs (Ctrl+C to exit logs, service will continue running)..."
docker compose -f docker-compose.yml -f dev.yml logs -f api