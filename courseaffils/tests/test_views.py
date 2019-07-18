from __future__ import unicode_literals

from datetime import time
from courseaffils.models import Course, CourseInfo
from courseaffils.tests.factories import (
    CourseFactory, UserFactory, GroupFactory
)
from courseaffils.tests.mixins import LoggedInFacultyTestMixin
from courseaffils.views import get_courses_for_user, get_courses_for_instructor
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.test import TestCase


class ViewTests(TestCase):

    def test_root(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 404)

    def test_get_courses(self):
        course = CourseFactory()
        student = UserFactory()
        instructor = UserFactory()
        staff = UserFactory(is_staff=True)

        course.group.user_set.add(student)
        course.group.user_set.add(instructor)
        course.faculty_group.user_set.add(instructor)

        # as student
        lst = get_courses_for_user(student)
        self.assertEquals(len(lst), 1)
        self.assertTrue(course in lst)

        lst = get_courses_for_instructor(student)
        self.assertEquals(len(lst), 0)

        # as instructor
        lst = get_courses_for_user(instructor)
        self.assertEquals(len(lst), 1)
        self.assertTrue(course in lst)

        lst = get_courses_for_instructor(instructor)
        self.assertEquals(len(lst), 1)
        self.assertTrue(course in lst)

        # as staff
        lst = get_courses_for_user(staff)
        self.assertEquals(len(lst), 1)
        self.assertTrue(course in lst)

        lst = get_courses_for_instructor(staff)
        self.assertEquals(len(lst), 1)
        self.assertTrue(course in lst)


class CourseListViewTests(TestCase):
    def test_select_course_empty(self):
        response = self.client.get(reverse('select_course'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 0)

    def test_select_course(self):
        u = UserFactory(username='test')
        self.client.login(username='test', password='test')

        c = CourseFactory(title='My Course')

        response = self.client.get(reverse('select_course'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 0)
        response = self.client.get(reverse('select_course'),
                                   {'semester_view': 'sandbox'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context['object_list']), 0,
            'Non-staff users shouldn\'t see sandbox courses '
            'they aren\'t part of.')

        u.groups.add(c.group)
        response = self.client.get(reverse('select_course'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 0)
        response = self.client.get(reverse('select_course'),
                                   {'semester_view': 'sandbox'})
        self.assertEqual(
            len(response.context['object_list']), 1,
            'Non-staff users should see sandbox courses '
            'they are grouped with.')
        self.assertEqual(
            response.context['object_list'][0].title,
            'My Course')

    def test_select_course_staff(self):
        UserFactory(username='test', is_staff=True)
        self.client.login(username='test', password='test')

        CourseFactory(title='My Course')

        response = self.client.get(reverse('select_course'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 0)
        response = self.client.get(reverse('select_course'),
                                   {'semester_view': 'sandbox'})
        self.assertEqual(len(response.context['object_list']), 1)
        self.assertEqual(
            response.context['object_list'][0].title,
            'My Course')


class CourseCreateViewFacultyTests(TestCase, LoggedInFacultyTestMixin):
    def test_get(self):
        response = self.client.get(reverse('create_course'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        group = GroupFactory()

        self.assertEqual(Course.objects.count(), 0)
        self.assertEqual(CourseInfo.objects.count(), 0)
        response = self.client.post(reverse('create_course'), {
            'title': 'My Title',
            'group': group.pk,
            'faculty_group': group.pk,
            'term': 1,
            'year': 2016,
            'days': 'TR',
            'starttime': time(hour=16),
            'endtime': time(hour=18),
        })
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Course.objects.count(), 1)
        course = Course.objects.first()
        self.assertEqual(course.title, 'My Title')

        self.assertEqual(CourseInfo.objects.count(), 1)
        info = course.info
        self.assertEqual(info, CourseInfo.objects.first())
        self.assertEqual(info.term, 1)
        self.assertEqual(info.year, 2016)
        self.assertEqual(info.days, 'TR')
        self.assertEqual(info.starttime, time(hour=16))
        self.assertEqual(info.endtime, time(hour=18))
