from pathlib import Path
import os
import environ
from datetime import timedelta
from utils.custom_logger import CustomLogger

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(DEBUG=(bool, True))

LOG_LEVEL = 'INFO'

logger = CustomLogger(level=LOG_LEVEL).get_logger()

CUSTOM_LOGGER = logger

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")

ALLOWED_HOSTS = ['*']

# Application definition
SYSTEM_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    # [Django-Rest-Framework]
    "rest_framework",
    'rest_framework.authtoken',
    "corsheaders",  # CORS
    "drf_yasg",  # swagger
    'django_apscheduler',
    ]

APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"  # Default
SCHEDULER_DEFAULT = True   #서버 올라가면 자동실행

CUSTOM_APPS = [
    "accounts.apps.AccountsConfig",
    "auths.apps.AuthsConfig",
    "foodiehotspots.apps.FoodiehotspotsConfig",
]

INSTALLED_APPS = SYSTEM_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # 액세스 토큰의 수명
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),  # 갱신토큰의 갱신수명
    'SLIDING_TOKEN_LIFETIME': timedelta(days=1),  # 갱신토큰의 수명
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.root_urls'

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

WSGI_APPLICATION = 'config.wsgi.application'


# Database
MYSQL_DB = env('MYSQL_DB')
if MYSQL_DB:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env("DB_NAME"),
            'USER': env("DB_USER"),
            'PASSWORD': env("DB_PASSWORD"),
            'HOST': env("DB_HOST"),
            'PORT': env("DB_PORT"),
        },
        # 'test': {
        #     'ENGINE': 'django.db.backends.mysql',
        #     'NAME': env("TEST_DB_NAME"),
        #     'USER': env("TEST_DB_USER"),
        #     'PASSWORD': env("TEST_DB_PASSWORD"),
        #     'HOST': env("TEST_DB_HOST"),
        #     'PORT': env("TEST_DB_PORT"),
        # },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    
CACHE_TTL = 60 * 1500    

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CACHE_TTL = 30  # Time to live

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        # 'BACKEND': 'django.core.cache.backends.cache.CacheClass',
        'LOCATION': 'redis://127.0.0.1:6379/1',  # Redis 서버 주소 및 포트
        # 'OPTIONS': {
        #     'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        # }
    }
}

# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_CACHE_ALIAS = "default"


# Password validation
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


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,      #디폴트 : True, 장고의 디폴트 로그 설정을 대체. / False : 장고의 디폴트 로그 설정의 전부 또는 일부를 다시 정의
    'formatters': {                        # message 출력 포맷 형식
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': { 
        'file': {
            'level': 'INFO',  #출력 레벨 설정
            'class': 'logging.FileHandler',  #파일 핸들러
            'filename': os.path.join(BASE_DIR,'logs/foodie.log'),
            'encoding': 'UTF-8',
            'formatter': 'verbose',  # 포맷터 수정
        },
    },
    'loggers': {
        'django': { 
                    'handlers': ['file'], 
                    'level': LOG_LEVEL,  #레벨
                    'propagate': True, 
        }, 
    }, 
}

# Internationalization
LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL='/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Customizing User model
AUTH_USER_MODEL = "accounts.User"


