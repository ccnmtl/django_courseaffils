from django.test import TestCase
from courseaffils.models import Course, CourseSettings
from courseaffils.models import CourseInfo, CourseAccess
from django.contrib.auth.models import Group, User


class ModelsSimpleTest(TestCase):
    """ test some basic happy paths through the models """
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

    def test_unicode(self):
        assert unicode(self.c) == "test course"

    def test_members(self):
        assert self.student in self.c.members

    def test_students(self):
        assert self.student in self.c.students

    def test_students_no_faculty(self):
        """ need this to get complete coverage on the .students()
        method, handling the case where there is no faculty group"""
        second_student_group = Group.objects.create(name="2nd student group")
        self.student.groups.add(second_student_group)
        nf_course = Course.objects.create(
            group=second_student_group,
            title="course with no faculty group")
        assert self.student in nf_course.students
        nf_course.delete()
        second_student_group.delete()

    def test_faculty(self):
        assert self.faculty in self.c.faculty

    def test_faculty_no_faculty(self):
        """ need this to get complete coverage on the .faculty()
        method, handling the case where there is no faculty group"""
        second_student_group = Group.objects.create(name="2nd student group")
        self.student.groups.add(second_student_group)
        nf_course = Course.objects.create(
            group=second_student_group,
            title="course with no faculty group")
        assert nf_course.faculty == ()
        nf_course.delete()
        second_student_group.delete()

    def test_user_set(self):
        assert self.student in self.c.user_set.all()

    def test_is_faculty(self):
        assert self.c.is_faculty(self.faculty)
        assert not self.c.is_faculty(self.student)

    def test_is_member(self):
        assert self.c.is_member(self.student)

    def test_is_true_member(self):
        assert self.c.is_true_member(self.student)

    def test_is_true_member_nonexistant(self):
        class StubUser(object):
            id = -1
        u = StubUser()
        assert not self.c.is_true_member(u)

    def test_faculty_filter(self):
        # TODO: I don't actually know what to do with this
        # I don't know what the faculty_filter is for
        # and it looks like it *ought* to not work,
        # since it's filtering on an "author" field that
        # shouldn't exist (or at least, I don't know where it's
        # supposed to be used). And I can't find a usage of this
        # anywhere else in the courseaffils code
        # for now, just execute it to at least get coverage
        self.c.faculty_filter
        assert True

    def test_default_slug(self):
        assert self.c.default_slug() == "test_course"

    def test_slug(self):
        # TODO: mock out django settings for this one
        # since it actually can change the behavior
        assert self.c.slug() == "test_course"

    def test_details(self):
        # shouldn't be any to start with
        assert self.c.details() == dict()
        self.c.add_detail("foo", "bar")
        assert "foo" in self.c.details()
        assert self.c.details()["foo"].value == "bar"
        assert self.c.get_detail("foo", default="not bar") == "bar"
        assert self.c.get_detail(
            "nonexistant",
            default="a default value") == "a default value"

        assert unicode(self.c.details()["foo"]) == "(test course) foo: bar"

        # update
        self.c.add_detail("foo", "baz")
        assert self.c.details()["foo"].value == "baz"

    def test_coursesettings(self):
        cs = CourseSettings.objects.create(
            course=self.c,
            custom_headers="some headers")
        assert unicode(cs) == "Settings for test course"

    def test_courseinfo(self):
        # current behavior is that a CourseInfo object
        # is created automatically for each course
        # by a hook elsewhere. so verify that.
        assert CourseInfo.objects.all().count() != 0

        self.assertEqual(unicode(self.c.info),
                         u'test course () None None-None')

        self.c.info.year = 2013
        self.c.info.term = 1
        self.c.info.days = "MWF"
        self.c.info.save()
        self.assertEqual(unicode(self.c.info),
                         u'test course (Spring 2013) MWF None-None')

        assert self.c.info.time() == 'MWF'

        assert self.c.info.display() == "Spring 2013 MWF None-None"

    def test_courseaccess(self):
        """ what is this? """

        # respond() should do nothing
        CourseAccess.respond("foo")
        assert True

        class StubRequest(object):
            REQUEST = dict()

        assert not CourseAccess.allowed(StubRequest())
