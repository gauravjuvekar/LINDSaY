"""
Django settings for lindsay project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Import runtime configuraton from project root generated at deployment
from .. import runtime_configuration
# This is a python file with the following parameters set
# SECRET_KEY
# ALLOWED_HOSTS
#
# DATABASE_NAME
# DATABASE_USER
# DATABASE_PASSWORD
## Optionally 
# DATABASE_HOST
# DATABASE_PORT
# 
# STATIC_ROOT




# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# NOTE: SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = runtime_configuration.SECRET_KEY

# NOTE: SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = runtime_configuration.ALLOWED_HOSTS


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.syndication',
    'mesg',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
)

ROOT_URLCONF = 'lindsay.urls'
LOGIN_URL = 'mesg:login'

WSGI_APPLICATION = 'lindsay.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': runtime_configuration.DATABASE_NAME,
        'USER': runtime_configuration.DATABASE_USER,
        'PASSWORD': runtime_configuration.DATABASE_PASSWORD
        #'HOST': '127.0.0.1',
        #'PORT': '3306',
    }
}


# Auth

AUTHENTICATION_BACKENDS = (
#    'django_auth_ldap.backend.LDAPbackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_LDAP_SERVER_URI = 'ldap://localhost:80'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = runtime_configuration.STATIC_ROOT
STATIC_URL = '/static/'
