#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run migrations automatically
python manage.py migrate

# Collect static files for admin panel and styles
python manage.py collectstatic --no-input