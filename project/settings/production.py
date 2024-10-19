from .base import *

DEBUG = False

ALLOWED_HOSTS = ['yourwebsite.com']

# Configurações adicionais específicas para produção
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True