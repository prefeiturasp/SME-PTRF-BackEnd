"""
Base settings to build other settings files upon.
"""

import datetime
import environ

# ROOT DIR E VARIÁVEIS DE AMBIENTE
# ------------------------------------------------------------------------------
ROOT_DIR = (
    environ.Path(__file__) - 3
)  # (sme_ptrf_apps/config/settings/base.py - 3 = sme_ptrf_apps/)
APPS_DIR = ROOT_DIR.path("sme_ptrf_apps")

env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR.path(".env")))

# CONFIGURAÇÕES BÁSICAS DO DJANGO
# ------------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", False)
TIME_ZONE = "America/Sao_Paulo"
LANGUAGE_CODE = "en-us"
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = False
LOCALE_PATHS = [ROOT_DIR.path("locale")]

# DATABASES
# ------------------------------------------------------------------------------
DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT'),
    }
}
DATABASES["default"]["ATOMIC_REQUESTS"] = True

# URLS
# ------------------------------------------------------------------------------
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "elasticapm.contrib.django",
    "corsheaders",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'admin_interface', # Para o django-admin-interface. Tem que estar antes do django.contrib.admin
    'colorfield',      # Para o django-admin-interface. Tem que estar antes do django.contrib.admin
    "django.contrib.admin",
    "django.forms",
    "django.contrib.postgres",
]
THIRD_PARTY_APPS = [
    "crispy_forms",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "rest_framework",
    "des",
    "auditlog",
    "django_celery_beat",
    "django_filters",
    "rangefilter",
    "ckeditor",
    "mathfilters",
    "drf_spectacular",
]

LOCAL_APPS = [
    "sme_ptrf_apps.core.apps.CoreConfig",
    "sme_ptrf_apps.users.apps.UsersConfig",
    "sme_ptrf_apps.despesas.apps.DespesasConfig",
    "sme_ptrf_apps.receitas.apps.ReceitasConfig",
    "sme_ptrf_apps.dre.apps.DreConfig",
    "sme_ptrf_apps.sme.apps.SmeConfig",
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIGRATIONS
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {"sites": "sme_ptrf_apps.contrib.sites.migrations"}

# PASSWORDS AND AUTHENTICATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_USER_MODEL = "users.User"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    "elasticapm.contrib.django.middleware.TracingMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "sme_ptrf_apps.jwt_middleware.JWTAuthenticationMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
]

# STATIC (DJANGO)
# ------------------------------------------------------------------------------
STATIC_ROOT = str(ROOT_DIR("staticfiles"))
STATIC_URL = "/django_static/"
STATICFILES_DIRS = [str(APPS_DIR.path("static"))]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# MEDIA (DJANGO)
# ------------------------------------------------------------------------------
MEDIA_ROOT = str(APPS_DIR("media"))
MEDIA_URL = "/media/"

# TEMPLATES (DJANGO)
# ------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR.path("templates"))],
        "OPTIONS": {
            "debug": True,
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "sme_ptrf_apps.utils.context_processors.settings_context",
            ],
        },
    }
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

CRISPY_TEMPLATE_PACK = "bootstrap4"

# FIXTURES
# ------------------------------------------------------------------------------
FIXTURE_DIRS = (str(APPS_DIR.path("fixtures")),)

# SECURITY CONFIGURATION
# ------------------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = 'des.backends.ConfiguredEmailBackend'

# ADMIN
# ------------------------------------------------------------------------------
ADMIN_URL = "admin/"
ADMINS = [("""Alessandro Fernandes""", "alessandro.fernandes@amcom.com.br")]
MANAGERS = ADMINS

# LOGGING CONFIGURATION
# ------------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
                      "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": env("DJANGO_LOG_LEVEL", default="INFO"),
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        'elasticapm': {
            'level': env('ELASTIC_APM_LOG_LEVEL', default='INFO'),
            'class': 'elasticapm.contrib.django.handlers.LoggingHandler',
        },
    },
    "root": {"level": env("DJANGO_LOG_LEVEL", default="INFO"), "handlers": ["console", "elasticapm"]},
    "loggers": {
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        # Errors logged by the SDK itself
        "sentry_sdk": {"level": "ERROR", "handlers": ["console"], "propagate": False},
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        'django': {
            'handlers': ['elasticapm'],
            'level': 'WARNING',
            'propagate': False,
        },
        'elasticapm.errors': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

# CELERY SETTINGS
# ------------------------------------------------------------------------------
if USE_TZ:
    CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_URL = env("REDIS_LOCATION")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_TIME_LIMIT = 5 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 60
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# DJANGO COMPRESSOR
# ------------------------------------------------------------------------------
INSTALLED_APPS += ["compressor"]
STATICFILES_FINDERS += ["compressor.finders.CompressorFinder"]

# DJANGO REST FRAMEWORK SETTINGS
# -------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
        # "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# DRF-SPECTACULAR SETTINGS
#--------------------------------------------------------------------------------
from sme_ptrf_apps import __version__ as api_version
SPECTACULAR_SETTINGS = {
    'TITLE': 'SigEscola API',
    'DESCRIPTION': 'API da aplicação Sig.Escola',
    'VERSION': api_version,
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': r'/api/',
}

# JWT settings
# ------------------------------------------------------------------------------
JWT_AUTH = {
    # TODO: rever a configuração...
    'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=100),
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(hours=100),
    'JWT_ALLOW_REFRESH': True,
}

# CORS SETTINGS
# ------------------------------------------------------------------------------
CORS_ORIGIN_ALLOW_ALL = True

# API TERCEIRIZADAS
# ------------------------------------------------------------------------------
EOL_API_TERCEIRIZADAS_URL = env('EOL_API_TERCEIRIZADAS_URL')
EOL_API_TERCEIRIZADAS_TOKEN = env('EOL_API_TERCEIRIZADAS_TOKEN')

# API SME_INTEGRACAO
# ------------------------------------------------------------------------------
SME_INTEGRACAO_URL = env('SME_INTEGRACAO_URL')
SME_INTEGRACAO_TOKEN = env('SME_INTEGRACAO_TOKEN')

# CORESSO
# ------------------------------------------------------------------------------
SYS_GRUPO_ID_UE=env('SYS_GRUPO_ID_UE')
SYS_GRUPO_ID_DRE=env('SYS_GRUPO_ID_DRE')
SYS_GRUPO_ID_SME=env('SYS_GRUPO_ID_SME')
SYS_GRUPO_ID_PTRF=env('SYS_GRUPO_ID_PTRF')

# CKEDITOR CONFIGS
# ------------------------------------------------------------------------------
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono',
        # 'skin': 'office2013',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_YourCustomToolbarConfig': [
            {'name': 'document', 'items': ['Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace', '-', 'SelectAll']},
            {'name': 'forms',
             'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
                       'HiddenField']},
            '/',
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert',
             'items': ['Image', 'Flash', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar', 'PageBreak', 'Iframe']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'tools', 'items': ['Maximize', 'ShowBlocks']},
            {'name': 'about', 'items': ['About']},
            '/',  # put this to force next toolbar on new line
            {'name': 'yourcustomtools', 'items': [
                # put the name of your editor.ui.addButton here
                'Preview',
                'Maximize',

            ]},
        ],
        'toolbar': 'YourCustomToolbarConfig',  # put selected toolbar config here
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage', # the upload image feature
            # your extra plugins here
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            # 'devtools',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
    }
}

# ELASTIC APM CONFIGS
# ------------------------------------------------------------------------------
ELASTIC_APM = {
    'SERVICE_NAME': env('ELASTIC_APM_SERVICE_NAME', default='SIG_ESCOLA_API'),
    'SECRET_TOKEN': env('ELASTIC_APM_SECRET_TOKEN', default=''),
    'DEBUG': env('ELASTIC_APM_DEBUG', default=False),
    'SERVER_URL': env('ELASTIC_APM_SERVER_URL', default='http://localhost:8200'),
    'ENVIRONMENT': env('ELASTIC_APM_ENVIRONMENT', default='local'),
    'ENABLED': env('ELASTIC_APM_ENABLED', default=False),
    'DISABLE_SEND': env('ELASTIC_APM_DISABLE_SEND', default=True),
}
