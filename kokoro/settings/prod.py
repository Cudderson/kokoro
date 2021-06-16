from .common import *

print("Running Prod Settings")

DEBUG = False

ADMINS = [
    ('Admin', os.getenv('ADMIN_EMAIL_ADDRESS'))
]
print(f"Admin email address: {os.getenv('ADMIN_EMAIL_ADDRESS')}")

# DEBUG = False requires allowed hosts
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
]

STATIC_ROOT = os.path.join(BASE_DIR, 'kokoro/staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'kokoro_app/static')
]

# Heroku settings
import django_heroku
django_heroku.settings(locals())
