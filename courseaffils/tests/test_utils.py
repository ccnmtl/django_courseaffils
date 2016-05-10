from django.test import TestCase
from courseaffils.utils import get_current_term
from freezegun import freeze_time


class TestUtils(TestCase):
    def test_get_current_term(self):
        with freeze_time('2016-01-01'):
            self.assertEqual(get_current_term(), 1)
        with freeze_time('2016-03-16'):
            self.assertEqual(get_current_term(), 1)
        with freeze_time('2016-04-30'):
            self.assertEqual(get_current_term(), 1)
        with freeze_time('2016-05-01'):
            self.assertEqual(get_current_term(), 1)
        with freeze_time('2016-05-20'):
            self.assertEqual(get_current_term(), 2)
        with freeze_time('2016-08-20'):
            self.assertEqual(get_current_term(), 2)
        with freeze_time('2016-09-02'):
            self.assertEqual(get_current_term(), 3)
        with freeze_time('2016-12-12'):
            self.assertEqual(get_current_term(), 3)
