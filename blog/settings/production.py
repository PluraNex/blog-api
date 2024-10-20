# project/settings/production.py
from .base import *
from dotenv import load_dotenv
import os

# Carregar variáveis do arquivo .env
load_dotenv()

DEBUG = os.getenv('PROD_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('PROD_ALLOWED_HOSTS', 'yourwebsite.com').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PROD_DB_NAME'),
        'USER': os.getenv('PROD_DB_USER'),
        'PASSWORD': os.getenv('PROD_DB_PASSWORD'),
        'HOST': os.getenv('PROD_DB_HOST'),
        'PORT': os.getenv('PROD_DB_PORT', '5432'),
    }
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
