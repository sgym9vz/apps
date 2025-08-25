#!/bin/bash

daphne -b 0.0.0.0 -p 8001 \
    -v 2 \
    --access-log - \
    django_intmd.asgi:application
