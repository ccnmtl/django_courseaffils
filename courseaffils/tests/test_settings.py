from __future__ import unicode_literals

from courseaffils.columbia import CourseStringMapper


SECRET_KEY = 'fake-key'
MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'courseaffils',
    'django_markwhat',
    'django_jenkins',
)

PROJECT_APPS = [
    'courseaffils',
]
COVERAGE_EXCLUDES_FOLDERS = ['migrations']

COURSEAFFILS_EXEMPT_PATHS = (
    '/accounts/',
    '/static/',
    '/site_media/',
    '/docs/',
    '/admin/',
    '/registration/',
    '/favicon.ico',
    '/smoketest/',
)
COURSEAFFILS_COURSESTRING_MAPPER = CourseStringMapper
ROOT_URLCONF = 'courseaffils.tests.urls'

# Django replaces this, but it still wants it. *shrugs*
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'HOST': '',
        'PORT': '',
        'USER': '',
        'PASSWORD': '',
    }
}
