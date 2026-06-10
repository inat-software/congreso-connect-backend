#!/bin/sh
set -e

echo "Running migrate..."
python manage.py migrate --noinput

echo "Starting Daphne..."
exec daphne -b 0.0.0.0 -p ${PORT:-8000} conf.asgi:application
