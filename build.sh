#!/usr/bin/env bash
# Script de build Render (cf. Guide_Deploy_Django_Render)
set -o errexit

pip install -r requirements.txt
python manage.py compilemessages
python manage.py collectstatic --no-input
python manage.py migrate

# Superutilisateur créé à partir des variables DJANGO_SUPERUSER_* (ignoré s'il existe déjà)
if [[ -n "$DJANGO_SUPERUSER_USERNAME" ]]; then
  python manage.py createsuperuser --no-input || true
fi
# Comptes de démonstration (optionnel)
if [[ "$SEED_DEMO" == "True" ]]; then
  python manage.py seed_demo
  python manage.py seed_food_rescue
  python manage.py seed_community
fi
