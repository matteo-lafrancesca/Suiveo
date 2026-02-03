# Utiliser une image Python officielle légère
FROM python:3.12-slim

# Définir le répertoire de travail
WORKDIR /app

# Empêcher Python d'écrire des fichiers .pyc et activer les logs non-bufferisés
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installer les dépendances système nécessaires pour psycopg2 et autres
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le script d'entrée
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Copier le reste du code de l'application
COPY . .

# Exposer le port (Gunicorn utilisera celui-ci)
EXPOSE 8000

# Définir le point d'entrée
ENTRYPOINT ["/app/entrypoint.sh"]
