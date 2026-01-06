"""
Django settings for click32 project.
"""

from pathlib import Path
import mimetypes
from datetime import datetime
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== SECURITY ====================

# SECURITY: TUDO por variáveis de ambiente
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-in-production') 
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Hosts dinâmicos por ambiente
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,62c21303ce5a.ngrok-free.app').split(',')

# CSRF dinâmico
csrf_origins = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,https://62c21303ce5a.ngrok-free.app').split(',')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins]

# WhatsApp number
WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '9999999999')

# ==================== APPLICATION ====================

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',  # ← ADICIONA WhiteNoise
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vitrine.click32_admin',
    'vitrine.apps.VitrineConfig',
    'django_prometheus',
    #'vitrine.templatetags',
    # 'compressor',  # ← REMOVE compressor
]

# ==================== MIDDLEWARE ====================

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← ADICIONA WhiteNoise
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'vitrine.middleware.HeartbeatLogFilter',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# Security settings baseados no DEBUG
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True') == 'True'  # ← Padrão True
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True') == 'True'  # ← Padrão True
CSRF_COOKIE_HTTPONLY = False  
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True 

mimetypes.add_type("application/manifest+json", ".json")

# ==================== TEMPLATES ====================

ROOT_URLCONF = 'click32.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug', 
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.csrf', 
            ],
        },
    },
]

WSGI_APPLICATION = 'click32.wsgi.application'

# ==================== DATABASE ====================

# Database: usa Postgres quando as env vars estão presentes; senão, fallback para SQLite (dev)
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

if POSTGRES_HOST and POSTGRES_DB:
    # Config para usar PostgreSQL (padrão para containers / produção)
    DATABASES = {
        "default": {
            'ENGINE': 'django_prometheus.db.backends.postgresql',
            "ENGINE": "django.db.backends.postgresql",
            "NAME": POSTGRES_DB or "click32_db",
            "USER": POSTGRES_USER or "click32_user",
            "PASSWORD": POSTGRES_PASSWORD or "click32_pass",
            "HOST": POSTGRES_HOST or "db",
            "PORT": POSTGRES_PORT,
            "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
            "ATOMIC_REQUESTS": os.getenv("DB_ATOMIC_REQUESTS", "True") == "True",
        }
    }
else:
    # Fallback para SQLite no desenvolvimento local (não requer configurar Postgres)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ==================== PASSWORD VALIDATION ====================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CORS_ALLOW_ALL_ORIGINS = os.getenv('CORS_ALLOW_ALL_ORIGINS', 'False') == 'True'

# ==================== INTERNATIONALIZATION ====================

# Internationalization - AJUSTADO PARA BRASIL
LANGUAGE_CODE = 'pt-br'  
TIME_ZONE = 'America/Sao_Paulo'   
USE_I18N = True
USE_TZ = True

# Formatação de datas e números para Brasil
USE_L10N = True
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i'
SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'

# Primeiro dia da semana = Segunda-feira
FIRST_DAY_OF_WEEK = 0  # 0 = Domingo, 1 = Segunda

# ==================== STATIC FILES (WHITENOISE) ====================

if DEBUG:
    WHITENOISE_MANIFEST_STRICT = False

LOGIN_URL = '/admin/login/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_MAX_AGE = 31536000  # 1 year cache for static files
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True  # Para desenvolvimento

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Remove compress finders - usa apenas os padrões do Django
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== LOGGING ====================

LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'heartbeat_filter': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: not (
                hasattr(record, 'request') and
                hasattr(record.request, 'path') and
                '/heartbeat/' in record.request.path and
                record.status_code == 200
            )
        },
        'console_heartbeat_filter': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: not (
                'POST /heartbeat/' in record.getMessage() and
                '200' in record.getMessage()
            )
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['console_heartbeat_filter'],
        },

        # 🔥 ALTERADO: FileHandler → TimedRotatingFileHandler
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(LOG_DIR, 'click32.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 14,
            'encoding': 'utf-8',
            'utc': False,
            # filtros aplicados apenas se quiserem (mantive igual ao original)
            # nenhum filtro existia aqui, então deixei como estava
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'stores': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'level': 'WARNING',
            'handlers': ['file'],
            'propagate': False,
        },
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
            'filters': ['console_heartbeat_filter'],
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
            'filters': ['console_heartbeat_filter'],
        },
    },
}
