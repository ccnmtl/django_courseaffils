from __future__ import unicode_literals

from courseaffils.middleware import CourseManagerMiddleware
from courseaffils.middleware import already_selected_course
from courseaffils.middleware import is_anonymous_path
from courseaffils.models import Course
from django.contrib.auth.models import Group, User
from django.http.response import Http404
from django.test import TestCase


class StubRequest(object):
    COOKIES = dict()
    GET = dict()
    POST = dict()
    environ = dict()

    def __init__(self, c):
        self.path = "/foo/bar"
        if c:
            self.session = {'ccnmtl.courseaffils.course': c}
        else:
            self.session = dict()

    def get_full_path(self):
        return self.path


class StubResponse(object):
    content = ""


class MiddlewareSimpleTest(TestCase):
    """
    These are really bad. courseaffils.middleware
    does a bunch of inspecting the settings
    directly, so it's hard to make tests that
    run independently of the application that
    is including it. Eg, for the moment,
    I run these tests from within mvsim,
    so it's testing those settings. We can
    improve this once we have a dedicated
    test harness for courseaffils, it will
    still be messy.
    """
    def setUp(self):
        self.student_group = Group.objects.create(name="studentgroup")
        self.faculty_group = Group.objects.create(name="facultygroup")
        self.student = User.objects.create(username="student",
                                           last_name="long enough")
        self.faculty = User.objects.create(username="faculty")
        self.student.groups.add(self.student_group)
        self.faculty.groups.add(self.faculty_group)
        self.c = Course.objects.create(
            group=self.student_group,
            title="test course",
            faculty_group=self.faculty_group)

    def test_is_anonymous_path(self):
        assert is_anonymous_path("/favicon.ico")
        assert not is_anonymous_path("/game")
        assert is_anonymous_path("/static/")

    def test_already_selected_course(self):
        assert already_selected_course(StubRequest(True))
        assert not already_selected_course(StubRequest(False))

    def test_cmm_process_response(self):
        c = CourseManagerMiddleware()
        assert c.process_response(StubRequest(True), "foo") == "foo"

    def test_cmm_process_response_anon(self):
        c = CourseManagerMiddleware()
        r = StubRequest(self.c)
        r.user = self.student
        r.COOKIES['ANONYMIZE'] = True
        r.scrub_names = {self.student: 1}
        resp = StubResponse()
        resp.content = str(self.student.get_full_name())
        assert "User Name" in c.process_response(r, resp).content
        resp.content = str(self.student.get_full_name())
        assert "long enough" not in c.process_response(r, resp).content

    def test_cmm_process_request(self):
        c = CourseManagerMiddleware()
        r = StubRequest(self.c)
        r.user = self.student
        assert c.process_request(r) is None

        r.path = "/favicon.ico"
        assert c.process_request(r) is None

        r = StubRequest(self.c)
        r.user = self.student
        r.GET['unset_course'] = True
        assert c.process_request(r) is None

        r = StubRequest(self.c)
        r.user = self.student
        r.POST['set_course'] = 'studentgroup'
        assert c.process_request(r) is None

        r = StubRequest(self.c)
        r.user = self.student
        r.POST['set_course'] = 'foobarbaz'
        with self.assertRaises(Http404):
            c.process_request(r)

        r = StubRequest(self.c)
        r.user = self.student
        r.POST['set_course'] = 'studentgroup'
        r.GET['next'] = "/foo"
        assert c.process_request(r) is not None
