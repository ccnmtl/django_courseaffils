from django.test import TestCase
from courseaffils.lib import users_in_course, in_course
from courseaffils.lib import in_course_or_404
from courseaffils.lib import handle_public_name, get_public_name
from courseaffils.models import Course
from django.contrib.auth.models import Group, User


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
        assert self.student in users_in_course(self.c)

    def test_in_course(self):
        assert in_course(self.student, self.c)
        assert in_course(self.student, self.student_group)
        assert not in_course(self.faculty, self.student_group)

    def test_in_course_or_404(self):
        assert in_course_or_404(self.student, self.c)
        assert in_course_or_404(self.student, self.student_group)
        try:
            # expect it to raise an error
            in_course_or_404(self.faculty, self.student_group)
            assert False
        except:
            assert True

    def test_handle_public_name(self):
        r = DummyRequest()
        assert handle_public_name(self.student, r) == "student"
        r.COOKIES['ANONYMIZE'] = True
        assert handle_public_name(self.student, r).startswith("User Name_")

    def test_get_public_name(self):
        r = DummyRequest()
        assert get_public_name(self.student, r) == "student"

        assert get_public_name([self.student, ], r) == "student"
