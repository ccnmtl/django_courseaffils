from courseaffils.tests.factories import CourseFactory, UserFactory
from django.core.urlresolvers import reverse
from django.test import TestCase


class ViewTests(TestCase):
    def test_root(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 404)

    def test_select_course_empty(self):
        response = self.client.get(reverse('select_course'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(len(response.context['infoless_courses']), 0)

    def test_select_course(self):
        u = UserFactory(username='test')
        self.client.login(username='test', password='test')

        c = CourseFactory(title='My Course')

        response = self.client.get(reverse('select_course'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(
            len(response.context['infoless_courses']), 0,
            'Non-staff users shouldn\'t see sandbox courses '
            'they aren\'t part of.')

        u.groups.add(c.group)
        response = self.client.get(reverse('select_course'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(
            len(response.context['infoless_courses']), 1,
            'Non-staff users should see sandbox courses '
            'they are grouped with.')
        self.assertEqual(
            response.context['infoless_courses'][0].title,
            'My Course')

    def test_select_course_staff(self):
        UserFactory(username='test', is_staff=True)
        self.client.login(username='test', password='test')

        CourseFactory(title='My Course')

        response = self.client.get(reverse('select_course'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 0)
        self.assertEqual(len(response.context['infoless_courses']), 1)
        self.assertEqual(
            response.context['infoless_courses'][0].title,
            'My Course')
