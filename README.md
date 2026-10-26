# EcoAssiette

**Plateforme intelligente d'alimentation durable** - analysez vos repas, mesurez leur impact environnemental et adoptez des alternatives végétales adaptées à votre quotidien.

![Aperçu de la page d'accueil EcoAssiette](docs/images/ecoassiette-home.png)

## Pourquoi EcoAssiette ?

L'impact environnemental d'un repas est difficile à visualiser et les alternatives végétales ne sont pas toujours simples à intégrer. EcoAssiette transforme une recette ou une photo en informations concrètes : émissions de CO₂e, consommation d'eau, utilisation des terres, substitutions possibles et économies obtenues.

La plateforme accompagne ensuite l'utilisateur jusqu'à l'action avec des menus hebdomadaires, une liste de courses, des produits partenaires, des récompenses et des preuves de réalisation.

## Fonctionnalités principales

### Assistant de recette intelligent

- Analyse d'une recette en texte libre avec Gemini.
- Assistant vocal global relié en lecture seule aux repas, menus, points, Food Rescue et à la communauté.
- Interface français/anglais/arabe avec rendu RTL, et compréhension du tounsi parlé ou écrit.
- Extraction des ingrédients, catégories et quantités.
- Repli local déterministe lorsque l'API est indisponible.
- Correction manuelle avant validation.
- Brouillons automatiques, reprise et suppression.
- Compréhension contextuelle : `pain burger` reste un féculent, tandis que `hamburger` est traité comme un plat à végétaliser.
- Suggestions maison avec quantités, préparation et tutoriels vidéo.

### Impact environnemental

- Estimation du CO₂e, de l'eau et de l'utilisation des terres.
- Indication du risque de déforestation.
- Comparaison avant/après une substitution végétale.
- Historique des réductions réellement adoptées.
- Tableau de bord personnel.

> Les valeurs sont des estimations pédagogiques fondées sur des moyennes de catégories alimentaires. Elles ne constituent pas une analyse de cycle de vie propre à chaque marque.

### Alternatives et produits végétaux

- Recommandations de produits publiés par les sponsors.
- Correspondance par ingrédient et contexte de recette.
- Import administratif d'un produit depuis son URL officielle avec extraction assistée par IA.
- Nom, description, prix, marque, mots-clés et données nutritionnelles vérifiables.
- Utilisation d'un même produit dans plusieurs plats distincts : burger, bolognaise, tacos, keftas, wrap, curry, etc.

### Nutrition par portion

Chaque menu et chaque alternative affiche une estimation des calories, protéines, fibres, glucides et lipides. Les valeurs exactes d'un produit peuvent être saisies pour 100 g dans l'administration. En leur absence, EcoAssiette utilise un référentiel moyen et signale clairement qu'il s'agit d'une estimation.

### Planificateur écologique

- 14 créneaux par semaine : déjeuner et dîner.
- Objectif carbone hebdomadaire personnalisable.
- Menus végétaux générés par Gemini ou par le moteur local.
- Nouveau groupe de recettes à chaque régénération.
- Remplacement intelligent des repas trop émetteurs.
- Intégration des produits végétaux disponibles.
- Tutoriel vidéo pour chaque menu.
- Liste de courses agrégée et imprimable.

### Récompenses, preuves et bons partenaires

- Envoi d'une photo ou d'une vidéo comme preuve d'un repas réalisé.
- Validation administrative et attribution idempotente des points.
- Portefeuille avec historique des crédits et dépenses.
- Réservation de produits partenaires avec remise.
- Bon PDF contenant un code unique et un QR code.
- Page de vérification du bon et validation à usage unique par un administrateur autorisé.

### Food Rescue

- Publication de surplus alimentaires.
- Analyse IA du contenu, de l'urgence et des allergènes.
- Réservation réservée aux profils éligibles et validés.
- Adresse protégée jusqu'à l'acceptation.
- Code de collecte, double confirmation et points solidaires.
- Matching explicable selon la compatibilité, la ville, l'urgence, l'équité et la fiabilité.
- Détection de doublons et estimation du risque de non-collecte.
- Recettes anti-gaspillage et assistant privé avec moteur local gratuit en secours.
- Tableau de pilotage intelligent réservé aux administrateurs.

### Communauté

- Fil social accessible à tous les membres connectés.
- Publications texte et photo, profils publics et recherche.
- Génération optionnelle d'une illustration avec Stable Diffusion Turbo exécuté localement, sans API.
- Mentions `@utilisateur` avec suggestions et sélection du compte.
- J’aime, commentaires, repartage interne et partage par lien.
- Photos stockées sur Cloudflare R2 lorsque le stockage distant est configuré.
- Modération depuis l’administration Django et protections d’accès côté serveur.

### Comptes et accompagnement

- Rôles Citoyen, Nutritionniste et Administrateur.
- Inscription, confirmation d'e-mail et réinitialisation du mot de passe.
- Profil alimentaire : régime, goûts, exclusions, activité, foyer et objectif CO₂.
- Recommandations personnalisées et partage volontaire avec un nutritionniste.
- Journal d'audit et historique de connexion.

## Parcours utilisateur

```text
Profil alimentaire
       |
Analyse IA d'une recette
       |
Impact environnemental + nutrition
       |
Alternative maison ou produit végétal
       |
Repas validé -> preuve -> points
       |
Produit partenaire -> bon PDF + QR code
```

## Technologies

| Domaine | Technologies |
|---|---|
| Backend | Python 3.13, Django 5.2, Django REST Framework |
| IA | Google Gemini via API REST, moteurs locaux de secours |
| Données | PostgreSQL en production, SQLite en développement |
| Tâches | Celery + Redis en option, thread local par défaut |
| Frontend | Templates Django, HTML sémantique, CSS responsive, JavaScript natif |
| Documents | ReportLab pour les bons PDF et QR codes |
| Déploiement | Render, Gunicorn, Uvicorn, WhiteNoise |
| Qualité | Tests Django, Coverage, contrôles d'accessibilité |

## Installation locale

### Prérequis

- Python 3.12 ou 3.13 ;
- Git ;
- Redis uniquement si `USE_CELERY=True`.

### Windows PowerShell

```powershell
git clone https://github.com/onsjaouadi2-dotcom/ecoassiette.git
cd ecoassiette
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py seed_food_rescue
python manage.py seed_community
python manage.py runserver
```

### Linux ou macOS

```bash
git clone https://github.com/onsjaouadi2-dotcom/ecoassiette.git
cd ecoassiette
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py seed_food_rescue
python manage.py seed_community
python manage.py runserver
```

Ouvrez ensuite [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

### Génération d’images IA sans API

Le moteur d’images est optionnel et séparé des dépendances web afin de ne pas alourdir une installation classique :

```bash
pip install -r requirements-ai-local.txt
python manage.py prepare_image_model
```

La seconde commande télécharge une seule fois `stabilityai/sd-turbo` dans le cache local. Après ce téléchargement,
mettez `LOCAL_IMAGE_OFFLINE=True` dans `.env` pour interdire tout accès réseau pendant la génération. Le réglage
`LOCAL_IMAGE_DEVICE=auto` utilise CUDA si un GPU NVIDIA compatible est disponible, sinon le processeur.

## Comptes de démonstration

Après `python manage.py seed_demo` :

| Identifiant | Rôle | Mot de passe |
|---|---|---|
| `admin_eco` | Administrateur | `EcoDemo2026!` |
| `nutri_sarra` | Nutritionniste | `EcoDemo2026!` |
| `amine`, `yasmine`, `Arij` | Citoyen | `EcoDemo2026!` |

Ces identifiants sont destinés uniquement à la démonstration locale. Changez tous les mots de passe en production.

## Configuration

Copiez `.env.example` vers `.env`. Les principales variables sont :

```dotenv
DEBUG=True
SECRET_KEY=changez-moi
ALLOWED_HOSTS=localhost,127.0.0.1

# SQLite est utilisé si cette valeur est absente.
DATABASE_URL=

# Le moteur local prend automatiquement le relais sans clé.
GEMINI_API_KEY=
GEMINI_MODEL=gemini-flash-latest
GEMINI_TIMEOUT=60
ASSISTANT_RATE_LIMIT=12
ASSISTANT_AUDIO_MAX_BYTES=5242880

# Génération d'images locale et gratuite (aucune clé API).
LOCAL_IMAGE_MODEL=stabilityai/sd-turbo
LOCAL_IMAGE_DEVICE=auto
LOCAL_IMAGE_OFFLINE=False
LOCAL_IMAGE_STEPS=2
LOCAL_IMAGE_SIZE=512

USE_CELERY=False
REDIS_URL=redis://localhost:6379/0

# Optionnel : avatars et photos Food Rescue sur Cloudflare R2.
CLOUDFLARE_R2_ACCOUNT_ID=
CLOUDFLARE_R2_ACCESS_KEY_ID=
CLOUDFLARE_R2_SECRET_ACCESS_KEY=
CLOUDFLARE_R2_BUCKET=ecoassiette-media
CLOUDFLARE_R2_PUBLIC_URL=
```

Les cinq variables Cloudflare doivent être renseignées ensemble. Sinon, Django utilise automatiquement
le stockage local. Les avatars sont contrôlés, redimensionnés à 512 × 512 maximum et convertis en WebP.
Les secrets ne doivent jamais être ajoutés à Git.

## Commandes utiles

```bash
# Démarrer l'application
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Tests
python manage.py test
python manage.py test users repas impact planning food_rescue community

# Couverture
coverage run manage.py test
coverage report -m
coverage html
```

## Tester les langues et l'assistant vocal

1. Renseignez `GEMINI_API_KEY` dans `.env`, puis lancez `python manage.py runserver`.
2. Connectez-vous et ouvrez `/assistant/` ou cliquez sur **Assistant vocal**.
3. Testez une question texte dans chaque langue : `Combien de points ai-je ?`,
   `What surplus is available?`, puis `9adech 3andi points?` ou `شنوة فما متوفر؟`.
4. Autorisez le micro et parlez pendant moins de 30 secondes. Le micro exige HTTPS en
   production, mais fonctionne aussi sur `localhost`.
5. Choisissez **AR** dans l'en-tête pour vérifier la traduction et l'affichage RTL.

Sans clé Gemini, les questions texte courantes utilisent le moteur local. La transcription
audio nécessite Gemini. L'assistant accède en lecture seule à un résumé filtré des repas,
menus, points, dons, réservations et notifications du compte connecté. Les adresses privées,
codes de collecte, e-mails et données appartenant aux autres comptes sont exclus.

Tests ciblés :

```bash
python manage.py test voice_assistant
python manage.py check
python manage.py makemigrations --check --dry-run
```

## Structure du projet

```text
ecoassiette/
├── config/          # paramètres, URLs, ASGI/WSGI et Celery
├── users/           # comptes, rôles, profils, e-mails et recommandations
├── repas/           # suivi des repas et analyses photo/texte/audio
├── impact/          # impacts, alternatives, sponsors, points et bons PDF
├── planning/        # menus hebdomadaires et listes de courses
├── food_rescue/     # dons de surplus et collectes solidaires
├── community/       # fil social, mentions, likes, commentaires et partages
├── voice_assistant/ # conversation texte/audio Gemini et contexte utilisateur filtré
├── locale/          # catalogues anglais et arabe
├── templates/       # mise en page globale et composants partagés
├── static/          # CSS, JavaScript, polices et icônes
├── docs/images/     # captures utilisées par la documentation
├── requirements.txt
├── render.yaml
└── manage.py
```

## Intelligence artificielle responsable

EcoAssiette suit une chaîne de traitement contrôlée :

1. Gemini reçoit une consigne JSON structurée.
2. La réponse est validée par le serveur.
3. Les aliments évités et résultats non conformes sont filtrés.
4. Un moteur local prend le relais en cas d'absence de clé, timeout, quota ou réponse invalide.
5. L'utilisateur vérifie et corrige les données avant toute validation définitive.

L'IA ne certifie ni la sécurité sanitaire, ni la valeur médicale d'un conseil, ni l'analyse environnementale exacte d'une marque.

## Sécurité et confidentialité

- Authentification Django et mots de passe hachés.
- Autorisations contrôlées côté serveur pour chaque rôle.
- Isolation des repas, brouillons, preuves, plannings et bons par propriétaire.
- Formulaires protégés par CSRF ; actions sensibles en POST.
- QR codes aléatoires et bons utilisables une seule fois.
- Secrets chargés depuis l'environnement.
- ORM Django sans SQL brut.
- Cookies sécurisés, HSTS et redirection HTTPS en production.
- Export et suppression des données personnelles.

## Déploiement sur Render

Le dépôt contient `render.yaml` et `build.sh`.

1. Créez un Blueprint Render depuis le dépôt.
2. Configurez `SECRET_KEY`, `GEMINI_API_KEY` et les variables d'e-mail.
3. Render fournit `DATABASE_URL` à partir de PostgreSQL.
4. Le build installe les dépendances, collecte les fichiers statiques et applique les migrations.

Commande de démarrage :

```bash
python -m gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker
```

## Sources environnementales

Les facteurs de démonstration s'inspirent notamment de :

- Poore, J. & Nemecek, T. (2018), *Reducing food's environmental impacts through producers and consumers*, Science.
- Scarborough et al. (2014), étude des émissions alimentaires selon les régimes.

Les sources et facteurs doivent être revus avant toute utilisation scientifique, réglementaire ou commerciale.

## Contribution

1. Créez une branche depuis `main`.
2. Implémentez une fonctionnalité avec ses tests et migrations.
3. Exécutez `python manage.py test` et `python manage.py check`.
4. Ouvrez une pull request en décrivant le besoin, la solution et les vérifications effectuées.

## Licence

Projet pédagogique 5TWIN - Esprit, 2026. Ajoutez un fichier `LICENSE` avant toute diffusion publique ou commerciale.
