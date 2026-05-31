#!/usr/bin/env python3
"""
Script de démarrage rapide pour le projet PlaintesApp.
Lance l'installation, les migrations et crée un superutilisateur admin.
"""

import os
import subprocess
import sys

def run(cmd, check=True):
    print(f"\n>>> {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def main():
    print("=" * 60)
    print("  PlaintesApp - Installation & Démarrage")
    print("=" * 60)

    # 1. Install deps
    run(f"{sys.executable} -m pip install -r requirements.txt")

    # 2. Migrations
    run(f"{sys.executable} manage.py makemigrations plaintes")
    run(f"{sys.executable} manage.py migrate")

    # 3. Create superuser (admin / admin123)
    run(f"""{sys.executable} manage.py shell -c "
from django.contrib.auth.models import User
from plaintes.models import ProfilUtilisateur
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    u.first_name = 'Admin'
    u.last_name = 'Système'
    u.save()
    ProfilUtilisateur.objects.create(user=u, role='administrateur')
    print('Superutilisateur admin créé.')
else:
    print('Superutilisateur admin existe déjà.')
"
""")

    # 4. Create demo categories
    run(f"""{sys.executable} manage.py shell -c "
from plaintes.models import Categorie
cats = ['Voirie', 'Éclairage public', 'Propreté', 'Bruit', 'Eau et assainissement', 'Espaces verts', 'Autre']
for c in cats:
    Categorie.objects.get_or_create(nom=c)
print('Catégories créées.')
"
""")

    print("\n" + "=" * 60)
    print("  ✅ Installation terminée !")
    print()
    print("  Accès admin:")
    print("  URL      : http://127.0.0.1:8000/")
    print("  Login    : admin")
    print("  Mot passe: admin123")
    print()
    print("  Démarrage du serveur...")
    print("=" * 60)

    run(f"{sys.executable} manage.py runserver", check=False)

if __name__ == '__main__':
    main()
