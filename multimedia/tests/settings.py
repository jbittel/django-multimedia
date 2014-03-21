DEBUG = False
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = 'UTC'
USE_TZ = True

SECRET_KEY = '(n0u-2=rcdsh15ltm+@xp6#5wu0sr687!)26l1^-8h174*pu4e'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'filer',
    'multimedia',
)
