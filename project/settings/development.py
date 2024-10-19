# project/settings/development.py
from .base import *
from dotenv import load_dotenv
import os

# Carregar variáveis do arquivo .env
load_dotenv()

# Configurações específicas para Desenvolvimento
DEBUG = os.getenv('DEV_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('DEV_ALLOWED_HOSTS', 'localhost').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DEV_DB_NAME'),
        'USER': os.getenv('DEV_DB_USER'),
        'PASSWORD': os.getenv('DEV_DB_PASSWORD'),
        'HOST': os.getenv('DEV_DB_HOST'),
        'PORT': os.getenv('DEV_DB_PORT', '5432'),
    }
}
