
# SoftDesk API

**SoftDesk API** est une API RESTful développée avec **Django REST Framework**, permettant la gestion de projets, de tâches (issues) et de commentaires. Elle respecte les standards **OWASP**, le **RGPD**, et s'inscrit dans une démarche **Green Code** grâce à la mise en place d'une pagination efficace.

----------

## Fonctionnalités

-   Authentification via JWT (JSON Web Token)
    
-   Gestion des utilisateurs avec consentement RGPD
    
-   Création et gestion de projets
    
-   Ajout de contributeurs aux projets
    
-   Création et suivi d'issues avec priorités, tags et statuts
    
-   Commentaires sur les issues
    
-   Pagination intégrée
    
-   Permissions avancées selon le rôle (auteur, contributeur)
    
-   Système complet de tests automatisés
    

----------

## Installation

```bash
git clone https://github.com/AlBlanchard/softdesk_api.git
cd softdesk_api
pipenv install
pipenv shell
python manage.py migrate
python manage.py runserver

```

----------

## Documentation

Une documentation présentant les différentes routes est disponible.
Pour cela il suffit de lancer le serveur.

```bash
python mangane.py runserver

```

Puis avec son navigateur aller sur l'adresse locale à la racine du projet.

## Authentification JWT

### Obtenir un token

```
POST /api/token/

```

### Rafraîchir un token

```
POST /api/token/refresh/

```

----------

## Générer des données de test

```bash
python scripts/generate_fake_data.py

```

Deux utilisateurs seront créés, ainsi que 30 projets avec des issues et commentaires.

### L'auteur :

  

Nom d'utilsateur : 

> authortest

 
Mot de passe : 

> djangotest10

  

L'auteur a créé 30 projets, des issues et commentaires associés.

  

### Le contributeur :

  

Nom d'utilisateur : 

> contributortest

Mot de passe : 

> djangotest20

Le contributeur est ajouté comme contributeur sur les projets aléatoirement.
Il est très peu probable qu'il puisse accéder à tous les projets créés. 

### Supprimer les données de test

```bash
python scripts/clean_fake_data.py

```

----------

## Endpoints principaux

Ressource

Endpoint

Utilisateurs

`/api/users/`

Projets

`/api/projects/projects/`

Contributeurs

`/api/projects/projects/{id}/contributors/`

Issues

`/api/projects/projects/{id}/issues/`

Commentaires

`/api/projects/projects/{id}/issues/{id}/comments/`

> L’API supporte également les routes classiques sans nesting.

----------

## Sécurité & conformité

-   Authentification sécurisée (JWT)
    
-   Contrôle des accès (permissions selon rôle et ressource)
    
-   Age minimum vérifié à l’inscription (conformité RGPD)
    
-   Consentement explicite pour la collecte et le partage de données
    
-   Suppression complète des comptes utilisateurs (droit à l’oubli)
    

----------

## Green Code

-   Pagination pour limiter les requêtes lourdes
    
-   Réduction des charges serveur via endpoints optimisés
    
-   Aucun nesting excessif dans les réponses
    

----------

## Tests

Lancer l’ensemble des tests :

```bash
python manage.py test

```