""" run tests for coursaffils

$ virtualenv ve
$ ./ve/bin/pip install -r test_reqs.txt
$ ./ve/bin/python runtests.py
"""

from django.conf import settings
from django.core.management import call_command
from courseaffils.columbia import CourseStringMapper
import django


def main():
    # Dynamically configure the Django settings with the minimum necessary to
    # get Django running tests
    settings.configure(
        MIDDLEWARE_CLASSES=[
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'courseaffils',
            'django_markwhat',
            'django_jenkins',
        ),
        TEST_RUNNER='django.test.runner.DiscoverRunner',

        PROJECT_APPS=[
            'courseaffils',
        ],
        COVERAGE_EXCLUDES_FOLDERS=['migrations'],

        COURSEAFFILS_EXEMPT_PATHS=(
            '/accounts/',
            '/static/',
            '/site_media/',
            '/docs/',
            '/admin/',
            '/registration/',
            '/favicon.ico',
            '/smoketest/',
            ),
        COURSEAFFILS_COURSESTRING_MAPPER=CourseStringMapper,
        ROOT_URLCONF='courseaffils.tests.urls',

        # Django replaces this, but it still wants it. *shrugs*
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
                'HOST': '',
                'PORT': '',
                'USER': '',
                'PASSWORD': '',
                }
            }
    )

    django.setup()
    # Fire off the tests
    call_command('jenkins')

if __name__ == '__main__':
    main()
