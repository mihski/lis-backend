#!/bin/bash
python3 manage.py migrate

python3 manage.py collectstatic --noinput
gunicorn -c gunicorn.config.py django_core.asgi:application

python3 manage.py runserver
