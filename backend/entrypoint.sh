#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting backend container..."

# Function to wait for database
wait_for_db() {
    echo "Waiting for database to be ready..."

    # Use DATABASE_URL if available, otherwise fall back to individual variables
    if [ -n "$DATABASE_URL" ]; then
        echo "Using DATABASE_URL for connection..."
        while ! python -c "
import psycopg
import sys
import os
try:
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise Exception('DATABASE_URL not found')
    # psycopg3 uses plain postgresql:// URLs, no need to convert

    conn = psycopg.connect(database_url, connect_timeout=5)
    conn.close()
    print('Database connection successful')
    sys.exit(0)
except Exception as e:
    print(f'Database not ready: {e}')
    sys.exit(1)
"; do
            echo "Database not ready, waiting..."
            sleep 2
        done
    else
        echo "Using individual database environment variables..."
        local host=${DB_HOST:-postgres}
        local port=${DB_PORT:-5432}
        local user=${DB_USERNAME:-postgres}
        local db=${DB_NAME:-HipochondriAI}

        while ! python -c "
import psycopg
import sys
try:
    conn = psycopg.connect(
        host='$host',
        port='$port',
        user='$user',
        password='$DB_PASSWORD',
        dbname='$db',
        connect_timeout=5
    )
    conn.close()
    print('Database connection successful')
    sys.exit(0)
except Exception as e:
    print(f'Database not ready: {e}')
    sys.exit(1)
"; do
            echo "Database not ready, waiting..."
            sleep 2
        done
    fi

    echo "Database is ready!"
}

# Wait for database to be available
wait_for_db

# Run Alembic migrations
echo "Running database migrations..."
cd /app/app && alembic upgrade head

# Check if migrations were successful
if [ $? -eq 0 ]; then
    echo "Database migrations completed successfully."
else
    echo "Database migrations failed!"
    exit 1
fi

# Return to the app root directory
cd /app

# Start the application
echo "Starting FastAPI application..."
exec "$@"
