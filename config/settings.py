"""
Paramètres Django — EcoAssiette (plateforme d'alimentation durable).

Tous les secrets sont lus depuis les variables d'environnement (fichier .env
en local, variables Render en production). Aucun secret dans le code source.
"""
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


# --- Sécurité -----------------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-change-me")
DEBUG = env_bool("DEBUG", False)
TESTING = "test" in sys.argv

ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]
RENDER_EXTERNAL_HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()]
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RENDER_EXTERNAL_HOSTNAME}")

# Protections HTTPS activées uniquement en production réelle (Render ou HTTPS_ONLY=True),
# pour ne pas casser `runserver` en local (http://127.0.0.1).
if not DEBUG and (RENDER_EXTERNAL_HOSTNAME or env_bool("HTTPS_ONLY", False)):
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "3600"))
    SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True

# --- Applications ---------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "users.apps.UsersConfig",
    "repas",
    "impact",
    "planning.apps.PlanningConfig",
    "food_rescue.apps.FoodRescueConfig",
    "community.apps.CommunityConfig",
    "voice_assistant.apps.VoiceAssistantConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "builtins": ["users.templatetags.ui"],     # {% icon "…" %} partout, sans {% load %}
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "users.context_processors.notifications_admin",
                "users.context_processors.notifications_citoyen",
                "community.context_processors.notifications_communaute",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Base de données : SQLite en local, PostgreSQL (DATABASE_URL) sur Render ------
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# --- Authentification -------------------------------------------------------------
AUTH_USER_MODEL = "users.Utilisateur"
AUTHENTICATION_BACKENDS = [
    "users.backends.EmailOuUsernameBackend",
]
LOGIN_URL = "users:login"
LOGIN_REDIRECT_URL = "users:profil"
LOGOUT_REDIRECT_URL = "home"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalisation -------------------------------------------------------
LANGUAGE_CODE = "fr"
LANGUAGES = [
    ("fr", "Français"),
    ("en", "English"),
    ("ar", "العربية"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "Africa/Tunis"
USE_I18N = True
USE_TZ = True

# --- Fichiers statiques & médias (WhiteNoise) -------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG or TESTING
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
    },
}
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Cloudflare R2 (palier gratuit) : activé seulement quand toutes les variables
# sont présentes. En local et dans les tests, les médias restent sur disque.
R2_ACCOUNT_ID = os.getenv("CLOUDFLARE_R2_ACCOUNT_ID", "")
R2_ACCESS_KEY_ID = os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID", "")
R2_SECRET_ACCESS_KEY = os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY", "")
R2_BUCKET = os.getenv("CLOUDFLARE_R2_BUCKET", "")
R2_PUBLIC_URL = os.getenv("CLOUDFLARE_R2_PUBLIC_URL", "").rstrip("/")
if all((R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET, R2_PUBLIC_URL)):
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": R2_ACCESS_KEY_ID,
            "secret_key": R2_SECRET_ACCESS_KEY,
            "bucket_name": R2_BUCKET,
            "endpoint_url": f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
            "region_name": "auto",
            "signature_version": "s3v4",
            "querystring_auth": False,
            "custom_domain": urlparse(R2_PUBLIC_URL).netloc,
            "url_protocol": "https:",
            "file_overwrite": False,
        },
    }
    MEDIA_URL = f"{R2_PUBLIC_URL}/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Génération locale d'images communautaires, sans clé ni API externe.
LOCAL_IMAGE_MODEL = os.getenv("LOCAL_IMAGE_MODEL", "stabilityai/sd-turbo")
LOCAL_IMAGE_DEVICE = os.getenv("LOCAL_IMAGE_DEVICE", "auto")  # auto, cuda ou cpu
LOCAL_IMAGE_OFFLINE = env_bool("LOCAL_IMAGE_OFFLINE", False)
LOCAL_IMAGE_STEPS = int(os.getenv("LOCAL_IMAGE_STEPS", "2"))
LOCAL_IMAGE_SIZE = int(os.getenv("LOCAL_IMAGE_SIZE", "512"))

# --- E-mails ------------------------------------------------------------------------
# Choix automatique du backend. Les noms Django EMAIL_* et les noms MAIL_*
# (souvent utilisés dans les fichiers .env Laravel) sont tous les deux acceptés.
#   BREVO_API_KEY défini              -> API HTTPS Brevo
#   MAIL_MAILER=smtp ou identifiant   -> SMTP (Gmail + mot de passe d'application)
#   sinon                             -> console
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
MAIL_MAILER = os.getenv("MAIL_MAILER", "").strip().lower()
EMAIL_HOST = os.getenv("EMAIL_HOST") or os.getenv("MAIL_HOST") or "smtp.gmail.com"
EMAIL_PORT = int(os.getenv("EMAIL_PORT") or os.getenv("MAIL_PORT") or "587")
MAIL_ENCRYPTION = (os.getenv("MAIL_ENCRYPTION") or "tls").strip().lower()
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", MAIL_ENCRYPTION in ("tls", "starttls"))
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", MAIL_ENCRYPTION == "ssl")
if EMAIL_USE_TLS and EMAIL_USE_SSL:
    raise ValueError("EMAIL_USE_TLS et EMAIL_USE_SSL ne peuvent pas être activés ensemble.")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER") or os.getenv("MAIL_USERNAME", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD") or os.getenv("MAIL_PASSWORD", "")
# Google affiche les mots de passe d'application par groupes de quatre caractères.
if EMAIL_HOST.lower() == "smtp.gmail.com":
    EMAIL_HOST_PASSWORD = "".join(EMAIL_HOST_PASSWORD.split())
EMAIL_TIMEOUT = 15
if BREVO_API_KEY:
    EMAIL_BACKEND = "users.email_backends.BrevoBackend"
elif MAIL_MAILER == "smtp" or EMAIL_HOST_USER:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_FROM_ADDRESS = os.getenv("MAIL_FROM_ADDRESS") or EMAIL_HOST_USER or "no-reply@ecoassiette.tn"
EMAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "EcoAssiette").strip()
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", f"{EMAIL_FROM_NAME} <{EMAIL_FROM_ADDRESS}>")
# Confirmation obligatoire de l'e-mail à l'inscription. Mettre False quand aucun service
# d'envoi n'est disponible (ex. Render gratuit sans Brevo) : le compte est activé directement.
CONFIRMATION_EMAIL = env_bool("CONFIRMATION_EMAIL", True)
INVITATION_DUREE_HEURES = 48          # validité d'un lien d'invitation (nutritionniste)
# Durée de validité des liens (confirmation d'e-mail et réinitialisation) : 1 jour
PASSWORD_RESET_TIMEOUT = 60 * 60 * 24

# --- Django REST Framework ----------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# --- IA (Gemini) ---------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
GEMINI_TIMEOUT = int(os.getenv("GEMINI_TIMEOUT", "60"))
# Si le modèle principal est surchargé (HTTP 503 « high demand »), on essaie ces modèles dans l'ordre.
GEMINI_MODELES_SECOURS = [m.strip() for m in os.getenv(
    "GEMINI_MODELES_SECOURS", "gemini-2.5-flash,gemini-flash-lite-latest,gemini-2.5-flash-lite").split(",") if m.strip()]
# Délai par modèle : 3 essais tiennent dans les 90 s d'attente de la page
GEMINI_TIMEOUT_MODELE = int(os.getenv("GEMINI_TIMEOUT_MODELE", "25"))
ASSISTANT_AUDIO_MAX_BYTES = int(os.getenv("ASSISTANT_AUDIO_MAX_BYTES", str(5 * 1024 * 1024)))
ASSISTANT_RATE_LIMIT = int(os.getenv("ASSISTANT_RATE_LIMIT", "12"))

# --- Traitement asynchrone (Celery + Redis) -------------------------------------------
# USE_CELERY=True  -> la tâche IA est envoyée à un worker Celery (Redis).
# USE_CELERY=False -> repli : exécution dans un thread d'arrière-plan (pas de Redis requis).
USE_CELERY = env_bool("USE_CELERY", False)
CELERY_BROKER_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_TASK_TIME_LIMIT = 60
# Exécution synchrone forcée (tests)
IA_SYNCHRONE = env_bool("IA_SYNCHRONE", False)
# Laboratoire IA : pause entre deux appels Gemini (quota de l'offre gratuite) et nombre de phrases évaluées
GEMINI_PAUSE_S = float(os.getenv("GEMINI_PAUSE_S", "4"))
LABO_LIMITE_GEMINI = int(os.getenv("LABO_LIMITE_GEMINI", "40"))

# --- Journalisation (silencieuse pendant les tests)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "users": {"handlers": ["console"], "level": "CRITICAL" if TESTING else os.getenv("LOG_LEVEL", "INFO")},
        "repas": {"handlers": ["console"], "level": "CRITICAL" if TESTING else os.getenv("LOG_LEVEL", "INFO")},
        "food_rescue": {"handlers": ["console"], "level": "CRITICAL" if TESTING else os.getenv("LOG_LEVEL", "INFO")},
    },
}
