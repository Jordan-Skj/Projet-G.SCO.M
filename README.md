# G.SCO.M — Django

Migration du site original vers Django, avec les apps `home`, `news` et `contact`.
La sauvegarde originale complète et vérifiée se trouve dans `~/templates/Project-G.SCO.M`.
`static/style.css` est identique à l’original ; les images, transitions, menu mobile,
FAQ et navigation au défilement sont conservés.

## Démarrage

```bash
source .venv/bin/activate
# Pour une nouvelle installation :
pip install -r requirements.txt
# Copier .env.example vers .env uniquement si .env n’existe pas,
# puis remplacer SECRET_KEY par une valeur aléatoire privée.
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
DEBUG=True python manage.py runserver
```

- Accueil : `/`
- Actualités : `/news/` et `/news/<slug>/`
- Administration Unfold : `/admin/`
- Contact : POST `/contact/`, JSON pour AJAX et formulaire classique en secours.

Les migrations importent les trois actualités originales, dans leur ordre initial.
Le contenu détaillé initial reprend uniquement les textes disponibles dans le site source.
Compléter les articles dans l’administration. Les brouillons et publications futures
ne sont pas visibles publiquement. Les articles « à la une » apparaissent d’abord,
puis l’ordre d’affichage croissant, puis la date décroissante. L’accueil en affiche trois.
Les images téléversées remplacent automatiquement les images originales des articles.

## E-mails

Par défaut, le backend console écrit les messages dans le terminal : aucun e-mail
réel n’est envoyé. Pour activer SMTP, renseigner dans `.env` :

```dotenv
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.votre-fournisseur.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre-compte
EMAIL_HOST_PASSWORD=votre-secret
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=votre-adresse-autorisée
CONTACT_EMAIL=adresse-du-secrétariat
```

Le `.env` du projet University n’est pas modifié ; ses secrets et sa base de données
ne sont pas repris automatiquement dans ce projet indépendant.
L’adresse du visiteur est utilisée en Reply-To et non comme expéditeur SMTP.
Une réponse positive signifie que le backend a accepté le message, pas que sa livraison
finale est garantie. `.env`, SQLite, les téléversements et `.venv` sont ignorés par Git.

## Vérifications

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python manage.py collectstatic --noinput
```

Python utilisé : 3.14. Les versions installées sont figées dans `requirements.txt`.

Vérification Chromium effectuée à 1440 px et 390 px : mêmes dimensions de page
que l’original (10340 px et 18650 px de hauteur), sans erreur JavaScript.
Comparaison finale des captures : aucune différence de pixels à 1440 px et 390 px.
Menu mobile, FAQ, envoi AJAX, retour de succès et réactivation du bouton vérifiés.
Les médias téléversés ont également été vérifiés via HTTP en développement.

Les tests couvrent les pages, la visibilité des articles, les images téléversées,
l’administration, le formulaire avec/sans AJAX, CSRF et les échecs SMTP simulés.

## Déploiement

Configurer `DEBUG=False`, une clé privée, `ALLOWED_HOSTS`, SMTP,
`CSRF_TRUSTED_ORIGINS` (origines HTTPS) et `SECURE_SSL_REDIRECT=True`.
Les cookies sécurisés sont activés automatiquement avec `DEBUG=False`.
Configurer HSTS après validation HTTPS et sauvegarder la base SQLite et `media/`.
Les variables système priment sur `.env`. Le terminal de cette session définit
`DEBUG=release` : la commande de développement ci-dessus force explicitement `DEBUG=True`.
Utiliser un serveur WSGI/ASGI de production adapté à l’hébergement ; `runserver`
est uniquement destiné au développement. Exécuter migrations et collectstatic.
WhiteNoise sert les fichiers statiques compressés et versionnés ; en production,
le serveur web ou un stockage dédié doit servir `/media/` depuis `media/`.
Ne pas autoriser l’exécution des fichiers téléversés. Django sert les médias en développement.

Configuration conforme aux documentations [WhiteNoise](https://whitenoise.readthedocs.io/en/stable/django.html)
et [Unfold](https://unfoldadmin.com/docs/installation/quickstart/).

## Limites du contenu original

Les images `enseignant1.png`, `enseignant2.png`, `enseignant3.png`, `parent2.png`
et `parent3.png` étaient référencées mais absentes. Leurs emplacements sont conservés
sans remplacement visuel arbitraire. Ajouter les fichiers originaux dans
`static/assets/image/` pour les restaurer. L’image sociale absente utilise désormais
le logo existant, sans effet sur le rendu de la page.
Le bouton « Voir plus » des enseignants n’avait pas de comportement dans le site source.
Les coordonnées téléphoniques fictives d’origine sont conservées.
