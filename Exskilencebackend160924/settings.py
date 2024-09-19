"""
Django settings for Exskilencebackend160924 project.

Generated by 'django-admin startproject' using Django 4.1.13.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path

import certifi

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-7^i=nfbd72p=^)w^jk=*m#k7(84)o7sha1dfkmr9i4$65d0c6l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework', 
    'djongo',
    'Exskilence',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000', 
    'http://localhost:3001', 
    'https://surgefrontend.azurewebsites.net/',
    'https://internship24.azurewebsites.net/',
    'https://swapnodayaplacements.azurewebsites.net/',
    'https://surgemeetlink.azurewebsites.net/'
    'https://placements.exskilence.com/',
    'https://placements.exskilence.com',
    'https://exskilencetesting.azurewebsites.net/',
    
]

CSRF_TRUSTED_ORIGINS=[ 
    'https://surgefrontend.azurewebsites.net/',
    'https://internship24.azurewebsites.net/',
    'https://swapnodayaplacements.azurewebsites.net/',
    'https://surgemeetlink.azurewebsites.net/'
    'https://placements.exskilence.com/',
    'https://placements.exskilence.com',
    'https://exskilencetesting.azurewebsites.net/',
    ]

AZURE_ACCOUNT_NAME = 'storeholder'
AZURE_ACCOUNT_KEY = 'QxlUJdp8eSoPeQPas4NigSkXg6KMep7z+fPQ5CpPm0kRfjg7Q0lFmVEIyhU4ohFLFdSqntDAG6MY84elTfecnw=='
AZURE_CONTAINER = 'tpdata'

MSSQL_SERVER_NAME = 'slnkshmtbsil.database.windows.net'
MSSQL_DATABASE_NAME = 'exe_test'
MSSQL_USERNAME = 'tpssa'
MSSQL_PWD = 'TPSuser@sa123'
MSSQL_DRIVER =  'ODBC Driver 17 for SQL Server'

ROOT_URLCONF = 'Exskilencebackend160924.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Exskilencebackend160924.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'ExskilenceNEW',
        'ENFORCE_SCHEMA': False,  
        'CLIENT': {
            'host': 'mongodb+srv://kecoview:FVy5fqqCtQy3KIt6@cluster0.b9wmlid.mongodb.net/',
            'username': 'kecoview',
            'password': 'FVy5fqqCtQy3KIt6',
            'authMechanism': 'SCRAM-SHA-1',
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'kecoview@gmail.com'  # Replace with your Gmail address
EMAIL_HOST_PASSWORD = 'etbk kimg ghtn yjgj'  # Replace with your Gmail app password
EMAIL_TLS_CA_FILE = certifi.where()

 

