""" run tests for coursaffils

$ virtualenv ve
$ ./ve/bin/pip install Django==1.11.4
$ ./ve/bin/pip install -r test_reqs.txt
$ ./ve/bin/python runtests.py
"""

import os
from django.core.management import call_command
import django


def main():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'courseaffils.tests.test_settings'
    django.setup()
    # Fire off the tests
    call_command('jenkins')


if __name__ == '__main__':
    main()
