import os
import socket

from .dev import CommunityDevSettings
from .env_wrapper import env


class DockerBaseSettings(CommunityDevSettings):

    """Settings for local development with Docker"""

    DOCKER_ENABLE =env("DOCKER_ENABLE", True,is_bool=True)
    RTD_DOCKER_COMPOSE =env("RTD_DOCKER_COMPOSE", True,is_bool=True)
    RTD_DOCKER_COMPOSE_VOLUME = env("RTD_DOCKER_COMPOSE_VOLUME", 'selfhosted_build-user-builds')
    RTD_DOCKER_USER = f'{os.geteuid()}:{os.getegid()}'
    DOCKER_LIMITS = {'memory': '1g', 'time': 900}
    USE_SUBDOMAIN = env("USE_SUBDOMAIN", True,is_bool=True)

    PRODUCTION_DOMAIN = os.environ.get('RTD_PRODUCTION_DOMAIN', 'docs.c3sl.ufpr.br')
    PUBLIC_DOMAIN = os.environ.get('RTD_PUBLIC_DOMAIN', 'docs.c3sl.ufpr.br')
    PUBLIC_API_URL = f'http://{PRODUCTION_DOMAIN}'

    SLUMBER_API_HOST = env("SLUMBER_API_HOST", 'http://web:8000')
    SLUMBER_USERNAME = env("SLUMBER_USERNAME", 'admin')
    SLUMBER_PASSWORD = env("SLUMBER_PASSWORD", 'admin')

    RTD_EXTERNAL_VERSION_DOMAIN = env("RTD_EXTERNAL_VERSION_DOMAIN", 'build.docs.c3sl.ufpr.br')

    STATIC_URL = env("STATIC_URL", '/static/')

    # In the local docker environment, nginx should be trusted to set the host correctly
    USE_X_FORWARDED_HOST = env("USE_X_FORWARDED_HOST", True,is_bool=True)

    MULTIPLE_BUILD_SERVERS = ['build']

    # https://docs.docker.com/engine/reference/commandline/run/#add-entries-to-container-hosts-file---add-host
    # export HOSTIP=`ip -4 addr show scope global dev wlp4s0 | grep inet | awk '{print \$2}' | cut -d / -f 1`
    HOSTIP = os.environ.get('HOSTIP')

    # If the host IP is not specified, try to get it from the socket address list
    _, __, ips = socket.gethostbyname_ex(socket.gethostname())

    if ips and not HOSTIP:
        HOSTIP = ips[0][:-1] + "1"

    # Turn this on to test ads
    USE_PROMOS = env("USE_PROMOS", False,is_bool=True)
    ADSERVER_API_BASE = f'http://{HOSTIP}:5000'
    # Create a Token for an admin User and set it here.
    ADSERVER_API_KEY = env("ADSERVER_API_KEY", None)
    ADSERVER_API_TIMEOUT = env("ADSERVER_API_TIMEOUT", 2 )

    @property
    def DOCROOT(self):
        # Add an extra directory level using the container's hostname.
        # This allows us to run development environment with multiple builders (`--scale-build=2` or more),
        # and avoid the builders overwritting each others when building the same project/version

        return os.path.join(super().DOCROOT, socket.gethostname())

    # New templates
    @property
    def RTD_EXT_THEME_DEV_SERVER_ENABLED(self):
        return os.environ.get('RTD_EXT_THEME_DEV_SERVER_ENABLED') is not None

    @property
    def RTD_EXT_THEME_DEV_SERVER(self):
        if self.RTD_EXT_THEME_DEV_SERVER_ENABLED:
            return "http://assets.docs.c3sl.ufpr.br:10001"

    # Enable auto syncing elasticsearch documents
    ELASTICSEARCH_DSL_AUTOSYNC = 'SEARCH' in os.environ

    RTD_CLEAN_AFTER_BUILD = env("RTD_CLEAN_AFTER_BUILD", True,is_bool=True)

    @property
    def RTD_EMBED_API_EXTERNAL_DOMAINS(self):
        domains = super().RTD_EMBED_API_EXTERNAL_DOMAINS
        domains.extend([
            r'.*\.docs\.c3sl\.ufpr\.br',
            r'.*\.br\.ufpr\.c3sl\.docs\.build',
        ])

        return domains

    @property
    def LOGGING(self):
        logging = super().LOGGING
        logging['handlers']['console']['formatter'] = 'colored_console'
        logging['loggers'].update({
            # Disable Django access requests logging (e.g. GET /path/to/url)
            # https://github.com/django/django/blob/ca9872905559026af82000e46cde6f7dedc897b6/django/core/servers/basehttp.py#L24
            'django.server': {
                'handlers': ['null'],
                'propagate': False,
            },
            # Disable S3 logging
            'boto3': {
                'handlers': ['null'],
                'propagate': False,
            },
            'botocore': {
                'handlers': ['null'],
                'propagate': False,
            },
            's3transfer': {
                'handlers': ['null'],
                'propagate': False,
            },
            # Disable Docker API logging
            'urllib3': {
                'handlers': ['null'],
                'propagate': False,
            },
            # Disable gitpython logging
            'git.cmd': {
                'handlers': ['null'],
                'propagate': False,
            },
        })

        return logging

    @property
    def DATABASES(self):  # noqa
        return {
            "default": {
                "ENGINE": "django.db.backends.postgresql_psycopg2",
                "NAME": env("DBNAME","docs_db"),
                "USER": env("DBUSER", "docs_user"),
                "PASSWORD": env("DBPASSWORD", "docs_pwd"),
                "HOST": env("DBHOST", "database"),
                "PORT": env("DBPORT",""),
            },
            "telemetry": {
                "ENGINE": "django.db.backends.postgresql_psycopg2",
                "NAME": env("TELEMETRY_DBNAME","telemetry"),
                "USER": env("TELEMETRY_DBUSER", "docs_user"),
                "PASSWORD": env("TELEMETRY_DBPASSWORD", "docs_pwd"),
                "HOST": env("TELEMETRY_DBHOST", "database"),
                "PORT": env("TELEMETY_DBPORT","")
            },
        }

    def show_debug_toolbar(request):
        from django.conf import settings

        return settings.DEBUG

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': show_debug_toolbar,
    }

    ACCOUNT_EMAIL_VERIFICATION = env("ACCOUNT_EMAIL_VERIFICATION","none")
    SESSION_COOKIE_DOMAIN = env("SESSION_COOKIE_DOMAIN", None)
    CACHES = {
        'default': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': 'cache:6379',
        }
    }

    BROKER_URL = env("BROKER_URL","redis://cache:6379/0")
    CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND","redis://cache:6379/0")
    CELERY_RESULT_SERIALIZER = env("CELERY_RESULT_SERIALIZER","json")
    CELERY_ALWAYS_EAGER = env("CELERY_ALWAYS_EAGER", False,is_bool=True)
    CELERY_TASK_IGNORE_RESULT = env("CELERY_TASK_IGNORE_RESULT", False,is_bool=True)

    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    RTD_BUILD_MEDIA_STORAGE = 'readthedocs.storage.s3_storage.S3BuildMediaStorage'
    # Storage backend for build cached environments
    RTD_BUILD_ENVIRONMENT_STORAGE = 'readthedocs.storage.s3_storage.S3BuildEnvironmentStorage'
    # Storage backend for build languages
    RTD_BUILD_TOOLS_STORAGE = 'readthedocs.storage.s3_storage.S3BuildToolsStorage'
    # Storage for static files (those collected with `collectstatic`)
    STATICFILES_STORAGE = 'readthedocs.storage.s3_storage.S3StaticStorage'
    RTD_STATICFILES_STORAGE = 'readthedocs.storage.s3_storage.NoManifestS3StaticStorage'

    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID",'admin')
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY",'password')
    S3_MEDIA_STORAGE_BUCKET = env("S3_MEDIA_STORAGE_BUCKET",'media')
    S3_BUILD_COMMANDS_STORAGE_BUCKET = env("S3_BUILD_COMMANDS_STORAGE_BUCKET",'builds')
    S3_BUILD_ENVIRONMENT_STORAGE_BUCKET = env("S3_BUILD_ENVIRONMENT_STORAGE_BUCKET",'envs')
    S3_BUILD_TOOLS_STORAGE_BUCKET = env("S3_BUILD_TOOLS_STORAGE_BUCKET",'build-tools')
    S3_STATIC_STORAGE_BUCKET = env("S3_STATIC_STORAGE_BUCKET",'static')
    S3_STATIC_STORAGE_OVERRIDE_HOSTNAME = env("S3_STATIC_STORAGE_OVERRIDE_HOSTNAME",PRODUCTION_DOMAIN)
    S3_MEDIA_STORAGE_OVERRIDE_HOSTNAME = env("S3_MEDIA_STORAGE_OVERRIDE_HOSTNAME",PRODUCTION_DOMAIN)

    AWS_S3_ENCRYPTION = env("AWS_S3_ENCRYPTION", False,is_bool=True)
    AWS_S3_SECURE_URLS = env("AWS_S3_SECURE_URLS", False,is_bool=True)
    AWS_S3_USE_SSL = env("AWS_S3_USE_SSL", False,is_bool=True)
    AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL",'http://storage:9000/')
    AWS_QUERYSTRING_AUTH = env("AWS_QUERYSTRING_AUTH", False,is_bool=True)

    RTD_SAVE_BUILD_COMMANDS_TO_STORAGE = env("RTD_SAVE_BUILD_COMMANDS_TO_STORAGE", True,is_bool=True)
    RTD_BUILD_COMMANDS_STORAGE = 'readthedocs.storage.s3_storage.S3BuildCommandsStorage'
    BUILD_COLD_STORAGE_URL = env("BUILD_COLD_STORAGE_URL",'http://storage:9000/builds')

    STATICFILES_DIRS = [
        os.path.join(CommunityDevSettings.SITE_ROOT, 'readthedocs', 'static'),
        os.path.join(CommunityDevSettings.SITE_ROOT, 'media'),
    ]

    # Remove the checks on the number of fields being submitted
    # This limit is mostly hit on large forms in the Django admin
    DATA_UPLOAD_MAX_NUMBER_FIELDS = env("DATA_UPLOAD_MAX_NUMBER_FIELDS",None)

    # This allows us to have CORS work well in dev
    CORS_ORIGIN_ALLOW_ALL = env("CORS_ORIGIN_ALLOW_ALL", True,is_bool=True)
