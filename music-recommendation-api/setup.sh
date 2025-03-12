#!/bin/bash

echo "Setting up environment files..."

if [ ! -f .env.dev ]; then
    echo "Creating .env.dev from template"
    cp .env.example .env.dev
fi

if [ ! -f .env.stg ]; then
    echo "Creating .env.stg from template"
    cp .env.example .env.stg
    sed -i 's/ENVIRONMENT=dev/ENVIRONMENT=stg/g' .env.stg
fi

if [ ! -f .env ]; then
    echo "Creating .env (production) from template"
    cp .env.example .env
    sed -i 's/ENVIRONMENT=dev/ENVIRONMENT=prod/g' .env
fi


echo "Setting execute permissions for run scripts..."
chmod +x run-dev.sh
chmod +x run-stg.sh
chmod +x run-prod.sh

echo ""
echo "Setup complete!"
echo ""
echo "To run the application in different environments:"
echo "  - Development: ./run-dev.sh"
echo "  - Staging:     ./run-stg.sh"
echo "  - Production:  ./run-prod.sh"
echo ""
echo "Make sure to edit the environment files before running:"
echo "  - Development: .env.dev"
echo "  - Staging:     .env.stg"
echo "  - Production:  .env"
echo ""