from __future__ import unicode_literals

from django.test import TestCase
from courseaffils.lib import (
    faculty_courses_for_user,
    users_in_course, in_course,
    in_course_or_404, get_current_term,
    handle_public_name, get_public_name,
)
from courseaffils.models import Course
from django.contrib.auth.models import Group, User
from freezegun import freeze_time


class DummyRequest(object):
    COOKIES = dict()


class LibsSimpleTest(TestCase):
    def setUp(self):
        self.student_group = Group.objects.create(name="studentgroup")
        self.faculty_group = Group.objects.create(name="facultygroup")
        self.student = User.objects.create(username="student")
        self.faculty = User.objects.create(username="faculty")
        self.student.groups.add(self.student_group)
        self.faculty.groups.add(self.faculty_group)
        self.c = Course.objects.create(
            group=self.student_group,
            title="test course",
            faculty_group=self.faculty_group)

    def tearDown(self):
        self.c.delete()
        self.student_group.delete()
        self.faculty_group.delete()
        self.student.delete()
        self.faculty.delete()

    def test_users_in_course(self):
        self.assertIn(self.student, users_in_course(self.c))

    def test_in_course(self):
        self.assertTrue(in_course(self.student, self.c))
        self.assertTrue(in_course(self.student, self.student_group))
        self.assertFalse(in_course(self.faculty, self.student_group))

    def test_in_course_or_404(self):
        self.assertTrue(in_course_or_404(self.student, self.c))
        self.assertTrue(in_course_or_404(self.student, self.student_group))
        try:
            # expect it to raise an error
            in_course_or_404(self.faculty, self.student_group)
            assert False
        except:
            assert True

    def test_handle_public_name(self):
        r = DummyRequest()
        self.assertEqual(handle_public_name(self.student, r), "student")
        r.COOKIES['ANONYMIZE'] = True
        self.assertTrue(
            handle_public_name(self.student, r).startswith("User Name_"))

    def test_get_public_name(self):
        r = DummyRequest()
        self.assertEqual(get_public_name(self.student, r), "student")

        self.assertEqual(get_public_name([self.student, ], r), "student")

    def test_faculty_courses_for_user(self):
        faculty_courses = faculty_courses_for_user(self.faculty)
        student_courses = faculty_courses_for_user(self.student)

        self.assertEqual(faculty_courses.count(), 1)
        self.assertEqual(faculty_courses.first(), self.c)
        self.assertEqual(student_courses.count(), 0)
        self.assertEqual(student_courses.first(), None)


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
