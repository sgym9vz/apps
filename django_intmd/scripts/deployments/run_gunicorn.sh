#!/bin/sh

CPU_CORES=$(getconf _NPROCESSORS_ONLN)
WORKERS=$((CPU_CORES * 2 + 1))

echo "Starting Gunicorn with $WORKERS workers"

gunicorn django_intmd.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers $WORKERS \
    --log-level=info \
    --access-logfile=- \
    --error-logfile=- \
    --capture-output \
    --enable-stdio-inheritance