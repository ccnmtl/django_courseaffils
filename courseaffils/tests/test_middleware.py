from django.test import TestCase
from courseaffils.middleware import is_anonymous_path
from courseaffils.middleware import already_selected_course
from courseaffils.middleware import CourseManagerMiddleware


class StubRequest(object):
    COOKIES = dict()

    def __init__(self, v):
        if v:
            self.session = {'ccnmtl.courseaffils.course': 1}
        else:
            self.session = dict()


class SimpleTest(TestCase):
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

    def test_is_anonymous_path(self):
        assert is_anonymous_path("/favicon.ico")
        assert not is_anonymous_path("/game")
        assert is_anonymous_path("/static/")

    def test_already_selected_course(self):
        assert already_selected_course(StubRequest(True))
        assert not already_selected_course(StubRequest(False))

    def test_coursemanagermiddleware_process_response(self):
        c = CourseManagerMiddleware()
        assert c.process_response(StubRequest(True), "foo") == "foo"
