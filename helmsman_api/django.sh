#!/bin/bash
echo "Creating Migrations..."
python manage.py makemigrations djangoapp models

echo ====================================

echo "Starting Migrations..."
python manage.py migrate
echo ====================================

echo "Load seeds..."
python manage.py loaddata initial_data.json
#python manage.py loaddata data_for_demonstration.json
echo ====================================


echo "Starting Server..."
python manage.py runserver 0.0.0.0:8000
