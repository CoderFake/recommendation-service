#!/bin/bash

echo "Starting application in STAGING environment..."
docker compose -f docker-compose.yml -f stg.yml up -d

echo "Showing logs (Ctrl+C to exit logs, service will continue running)..."
docker compose -f docker-compose.yml -f stg.yml logs -f api