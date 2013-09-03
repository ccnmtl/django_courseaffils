from django.test import TestCase
from courseaffils.forms import CourseAdminForm
from django.contrib.auth.models import Group, User
from courseaffils.models import Course


class FormsSimpleTest(TestCase):
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

    def test_init(self):
        CourseAdminForm()
        CourseAdminForm(instance=self.c)

    def test_clean(self):
        s2 = Group.objects.create(name="studentgroup2")
        f = CourseAdminForm(
            dict(title="foo",
                 group=s2.id,
                 faculty_group=self.faculty_group.id,
                 add_user='student\n*nonexistant:foo',
                 ))
        f.save(commit=False)
        f.clean()
        f.clean_users_to_remove()
