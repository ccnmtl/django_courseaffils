from __future__ import unicode_literals

from django.contrib.auth.models import User

from courseaffils.tests.factories import UserFactory


class LoggedInSuperuserTestMixin(object):
    def setUp(self):
        self.u = User.objects.create_superuser(
            'superuser', 'admin@example.com', 'test')
        login = self.client.login(username='superuser', password='test')
        assert(login is True)


class LoggedInFacultyTestMixin(object):
    def setUp(self):
        self.u = UserFactory(username='test_faculty')
        self.u.set_password('test')
        self.u.save()
        login = self.client.login(username='test_faculty',
                                  password='test')
        assert(login is True)


class LoggedInStudentTestMixin(object):
    def setUp(self):
        self.u = UserFactory(username='test_student')
        self.u.set_password('test')
        self.u.save()
        login = self.client.login(username='test_student',
                                  password='test')
        assert(login is True)
