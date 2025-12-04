import os
import dj_database_url # Importante para la base de datos de Render

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SEGURIDAD:
# En producción (Render), DEBUG será False. En tu PC será True.
DEBUG = 'RENDER' not in os.environ

# SECRET_KEY:
# Render puede inyectar esto, si no, usa la por defecto 
SECRET_KEY = os.environ.get('SECRET_KEY', '-_&+lsebec(whhw!%n@ww&1j=4-^j_if9x8$q778+99oz&!ms2')

# ALLOWED_HOSTS:
# Render necesita '*' para aceptar tráfico desde su dominio onrender.com
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # WhiteNoise requiere esto
    'django_filters',             
    'rest_framework',
    'rest_framework.authtoken',   
    'corsheaders',                
    'control_escolar_desit_api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',         
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CONFIGURACIÓN CORS (Para Angular)
# Permitimos todo para evitar errores iniciales. 
# Luego puedes restringirlo a tu dominio de Angular en Render.
CORS_ALLOW_ALL_ORIGINS = True 
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'control_escolar_desit_api.urls'

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

WSGI_APPLICATION = 'control_escolar_desit_api.wsgi.application'

# BASE DE DATOS
# Lógica: Si Render nos da una DATABASE_URL, usamos PostgreSQL.
# Si no (estamos en local), usamos SQLite por defecto para evitar problemas con MySQL/my.cnf
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3'),
        conn_max_age=600
    )
}

# VALIDADORES DE CONTRASEÑA
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# INTERNACIONALIZACIÓN
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ARCHIVOS ESTÁTICOS (CSS, JS, IMAGES)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuración de almacenamiento para WhiteNoise (Comprime y cachea archivos)
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MEDIA FILES
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# REST FRAMEWORK
REST_FRAMEWORK = {
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'control_escolar_desit_api.models.BearerTokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
}