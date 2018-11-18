"""
WSGI config for ocado project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application
# INDISPENSABLE POUR FAIRE FONCTIONNER AVEC APACHE
sys.path.append('/Users/Vincent/PycharmProjects/ocado')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ocado.settings')

application = get_wsgi_application()
