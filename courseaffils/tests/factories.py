from __future__ import unicode_literals

import factory
from courseaffils.models import Affil, Course
from django.contrib.auth.models import User, Group


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'user%03d' % n)
    password = factory.PostGenerationMethodCall('set_password', 'test')
    email = factory.LazyAttribute(lambda u: '%s@example.com' % u.username)


class GroupFactory(factory.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: 'Example Group %d' % n)


class CourseFactory(factory.DjangoModelFactory):
    class Meta:
        model = Course

    title = factory.Sequence(lambda n: 'Example Course %d' % n)
    group = factory.SubFactory(GroupFactory)
    faculty_group = factory.SubFactory(GroupFactory)


class AffilFactory(factory.DjangoModelFactory):
    class Meta:
        model = Affil

    name = factory.Sequence(
        lambda n: 't1.y2016.s001.cf100%d.scnc.st.course:columbia.edu' % n)
    user = factory.SubFactory(UserFactory)
