#!/bin/bash
echo "Building Vercel Native Deployment..."

# Install dependencies
python3 -m pip install -r requirements.txt

# Make migrations and apply them
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

# Collect static files
python3 manage.py collectstatic --noinput
