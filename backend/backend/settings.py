from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Required configuration - no fallbacks
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable is required. Please set it in your .env file.")

DEBUG = os.getenv('DEBUG', 'False').lower() == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS')
if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS environment variable is required. Please set it in your .env file.")
ALLOWED_HOSTS = ALLOWED_HOSTS.split(',')

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'corsheaders',
    'knowledge',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'backend.middleware.ApiTrailingSlashMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS')
if not CORS_ALLOWED_ORIGINS:
    raise ValueError("CORS_ALLOWED_ORIGINS environment variable is required. Please set it in your .env file.")
CORS_ALLOWED_ORIGINS = CORS_ALLOWED_ORIGINS.split(',')
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'backend.urls'

WSGI_APPLICATION = 'backend.wsgi.application'

# CognoDB (Neo4j) Connection Settings - required
NEO4J_URI = os.getenv('NEO4J_URI')
if not NEO4J_URI:
    raise ValueError("NEO4J_URI environment variable is required. Please set it in your .env file.")

NEO4J_USER = os.getenv('NEO4J_USER')
if not NEO4J_USER:
    raise ValueError("NEO4J_USER environment variable is required. Please set it in your .env file.")

NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
if not NEO4J_PASSWORD:
    raise ValueError("NEO4J_PASSWORD environment variable is required. Please set it in your .env file.")

DATABASES = {}

AUTHENTICATION_BACKENDS = [
    'users.authentication.CognoDBAuthenticationBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'UNAUTHENTICATED_USER': None,
}
