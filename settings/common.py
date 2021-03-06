"""
Django settings for airtkts project.

For more information on this file, see
https://docs.djangoproject.com/en//topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en//ref/settings/
"""

import os

#==============================================================================
# Generic Django project settings
#==============================================================================

SITE_ID = 1

DEFAULT_FROM_EMAIL = 'noreply@aramael.com'

# A tuple that lists people who get code error notifications. When DEBUG=False and a view raises an exception, Django
# will email these people with the full exception information. Each member of the tuple should be a tuple of
# (Full name, email address). Note that Django will email all of these people whenever an error happens.
ADMINS = (
    ('Aramael Pena-Alcantara','aramael@pena-alcantara.com'),
)

# A tuple in the same format as ADMINS that specifies who should get broken link notifications when
# BrokenLinkEmailsMiddleware is enabled.
MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'south',
    'gunicorn',
    'guardian',
    'storages',
    'raven.contrib.django.raven_compat',
    'widget_tweaks',
    'airtkts.apps.events',
    'airtkts.libs.forms',
    'airtkts.libs.users',
)

#==============================================================================
# Calculation of directories relative to the project module location
#==============================================================================

ENVIRONMENT = os.getenv('ENVIRONMENT', 'DEVELOPMENT')

SETTINGS_DIR, filename = os.path.split(os.path.abspath(__file__))

SITE_ROOT = os.path.dirname(SETTINGS_DIR)

#==============================================================================
# Authentication settings
#==============================================================================

# The URL where requests are redirected after login when the contrib.auth.login view gets no next parameter.
# This is used by the login_required() decorator, for example.
LOGIN_REDIRECT_URL = 'accounts_home'

# The URL where requests are redirected for login, especially when using the login_required() decorator.
LOGIN_URL = 'auth_login'

# LOGIN_URL counterpart.
LOGOUT_URL = 'auth_logout'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # this is default
    'guardian.backends.ObjectPermissionBackend',
)

ANONYMOUS_USER_ID = -1

REPLACE_BUILTIN_IF = True

#==============================================================================
# Project URLS and Media settings
#==============================================================================

# Python dotted path to the URLCONF used by Django.
ROOT_URLCONF = 'airtkts.urls'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_ROOT, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

#==============================================================================
# Templates
#==============================================================================

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request"
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_ROOT, 'templates'),
)

#==============================================================================
# Middleware
#==============================================================================

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

from memcacheify import memcacheify

CACHES = memcacheify()

#==============================================================================
# Miscellaneous Project Settings
#==============================================================================

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'airtkts.wsgi.application'


RAVEN_CONFIG = {
    'dsn': 'https://bfb900dac1e44f7599684b76cd4f6d53:b6158e89ce3640428c91be38b650ff00@app.getsentry.com/14584',
}

#==============================================================================
# Logging
#==============================================================================

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
            },
        }
}