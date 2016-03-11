from django.core.urlresolvers import reverse
from django.test import TestCase


class ViewTests(TestCase):
    def test_root(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 404)

    def test_select_course(self):
        response = self.client.get(reverse('select_course'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['courses']), 0)
        self.assertEqual(len(response.context['current_courses']), 0)
