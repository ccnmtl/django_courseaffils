from __future__ import unicode_literals

from django import forms
from django.test import TestCase, override_settings
from django.contrib.auth.models import Group, User
from courseaffils.columbia import CourseStringMapper
from courseaffils.forms import CourseAdminForm
from courseaffils.models import Course


@override_settings(COURSEAFFILS_COURSESTRING_MAPPER=CourseStringMapper)
class FormsSimpleTest(TestCase):
    def setUp(self):
        self.student_group = Group.objects.create(name="studentgroup")
        self.faculty_group = Group.objects.create(name="facultygroup")

        self.student = User.objects.create(username="student",
                                           last_name="long enough")
        self.student.groups.add(self.student_group)

        # faculty are part of both student & faculty groups
        self.faculty = User.objects.create(username="faculty")
        self.faculty.groups.add(self.student_group)
        self.faculty.groups.add(self.faculty_group)

        self.c = Course.objects.create(
            group=self.student_group,
            title="test course",
            faculty_group=self.faculty_group)

    def test_init(self):
        CourseAdminForm()
        CourseAdminForm(instance=self.c)

    def test_clean(self):
        s2 = Group.objects.create(name="studentgroup2")
        f = CourseAdminForm(
            dict(title="foo",
                 group=s2.id,
                 faculty_group=self.faculty_group.id,
                 add_user='student\n*nonexistant:foo'
                 ))
        f.save(commit=False)
        f.clean()
        f.clean_users_to_remove()

        self.assertTrue(s2 in self.student.groups.all())
        self.assertFalse(self.faculty_group in self.student.groups.all())

        user = User.objects.filter(username='nonexistant').first()
        self.assertIsNotNone(user)
        self.assertTrue(s2 in user.groups.all())
        self.assertTrue(self.faculty_group in user.groups.all())

    def test_clean_no_group(self):
        f = CourseAdminForm(
            dict(title="foo",
                 faculty_group=self.faculty_group.id,
                 add_user='student\n*nonexistant:foo')
        )

        with self.assertRaisesRegexp(
                ValueError,
                'The Course could not be created'):
            f.save(commit=False)

        with self.assertRaisesRegexp(
                forms.ValidationError,
                'You must select a group or enter a course string'):
            f.clean()

    def test_clean_remove(self):
        f = CourseAdminForm(instance=self.c)
        f.cleaned_data = dict(pk=self.c.id,
                              title="test course",
                              group=self.student_group.id,
                              faculty_group=self.faculty_group.id,
                              add_user='',
                              users_to_remove=[self.faculty, self.student]
                              )
        f.save(commit=False)
        f.clean()
        f.clean_users_to_remove()

        self.assertFalse(self.student_group in self.student.groups.all())

        self.assertFalse(self.student_group in self.faculty.groups.all())
        self.assertFalse(self.faculty_group in self.faculty.groups.all())
