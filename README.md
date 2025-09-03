
# SmartSahaProject

## Description

SmartSahaProject est une application web développée avec Django, qui utilise le framework Django REST pour créer une API. Ce projet est conçu pour gérer des données relatives à des cultures, des messages, des parcelles, des publications, des tâches et des utilisateurs.

## Prérequis

Avant de commencer, assurez-vous d'avoir installé les éléments suivants :

- Python 3.x
- PostgreSQL
- pip

## Installation

1. Clonez le dépôt :

   ```bash
   git clone https://github.com/votre-utilisateur/SmaartSahaProject.git
   cd SmaartSahaProject
   ```
Créez un environnement virtuel et activez-le :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows utilisez `venv\Scripts\activate`
```
Installez les dépendances :
```bash
pip install -r requirements.txt
```
Configurez la base de données dans SmaartSahaProject/settings.py :
```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'geodb',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5433',
    }
}
```
Appliquez les migrations :
```bash
python manage.py migrate
```
Créez un super utilisateur pour accéder à l'interface d'administration :
```bash
python manage.py createsuperuser
```
Démarrez le serveur de développement :
```bash
python manage.py runserver
```
Utilisation
Accédez à l'application via votre navigateur à l'adresse http://127.0.0.1:8000/. Vous pouvez également accéder à l'interface d'administration à http://127.0.0.1:8000/admin/.

Structure du projet
```bash
SmaartSahaProject/
├── .github/
│   └── workflows/
│       └── python-package.yml
├── .idea/
├── SmartSaha/
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models/
│   ├── serializers/
│   ├── services/
│   ├── tests/
│   └── views/
├── SmaartSahaProject/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── docker-compose.yml
├── manage.py
└── requirements.txt
```

Contribuer
Les contributions sont les bienvenues ! N'hésitez pas à soumettre une demande de tirage (pull request).

License
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
