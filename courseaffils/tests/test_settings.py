from __future__ import unicode_literals

from courseaffils.columbia import CourseStringMapper


SECRET_KEY = 'fake-key'
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
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
