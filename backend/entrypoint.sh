#!/bin/sh

# Attendre que la base de données soit prête (si on utilise PostgreSQL)
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Appliquer les migrations de base de données
echo "Applying database migrations..."
python manage.py migrate

# Collecter les fichiers statiques (si besoin pour l'admin Django)
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Lancer le serveur
# En production (DEBUG=False), on utilise Gunicorn
if [ "$DEBUG" = "False" ]; then
    echo "Starting Gunicorn..."
    exec gunicorn suiveo_api.wsgi:application --bind 0.0.0.0:8000
else
    echo "Starting Django Development Server..."
    exec python manage.py runserver 0.0.0.0:8000
fi
