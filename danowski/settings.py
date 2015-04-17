"""
Django settings for danowski project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Application definition

INSTALLED_APPS = [
    'django_admin_bootstrapped',
    #### default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #### local dependencies
    # -
    #### local apps
    'danowski.apps.admin',
    'danowski.apps.geo',
    'danowski.apps.people',
    'danowski.apps.journals',
    'danowski.apps.network',
    # uncomment in your greatest time of need!
    # (migrating partial data from one DB to another, hopefully we never
    # need this again)
    #'fixture_magic',
]

TEMPLATE_CONTEXT_PROCESSORS = (
    # Default processors##############################
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    ##################################################
    "django.core.context_processors.request",
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

ROOT_URLCONF = 'danowski.urls'

WSGI_APPLICATION = 'danowski.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'sitemedia'),
]


# used with admin_reorder template tag
ADMIN_REORDER = (
    ("auth", ('Group', 'User')),
    ("geo", ('Location')),
    ("people", ('Person', 'School')),
    ("journals", ('Journal', 'Issue', 'IssueItem', 'Genre'))
)


# import localsettings
# This will override any previously set value
try:
    from localsettings import *
except ImportError:
    import sys
    print >> sys.stderr, '''Settings not defined. Please configure a version
        of localsettings.py for this site. See localsettings.py.dist for
        setup details.'''

# load & configure django_nose if available

django_nose = None
try:
    # NOTE: errors if DATABASES is not configured (in some cases),
    # so this must be done after importing localsettings
    import django_nose
except ImportError:
    print 'django nose import error'
    pass

# - only if django_nose is installed, so it is only required for development
if django_nose is not None:
    INSTALLED_APPS.append('django_nose')
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    # currently no plugins or extra command line options needed


