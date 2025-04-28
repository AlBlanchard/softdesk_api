# SoftDesk API

API RESTful développée en Django REST Framework pour la gestion de projets, de problèmes (issues) et de commentaires.

## Installation

```bash
git clone https://github.com/AlBlanchard/softdesk_api.git
cd softdesk_api
pipenv install
pipenv shell
python manage.py migrate
python manage.py runserver
```

## Pour générer des données tests

```bash
python scripts/generate_fake_data.py
```

```bash
python scripts/clean_fake_data.py
```   