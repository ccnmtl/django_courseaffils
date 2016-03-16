import factory
from courseaffils.models import Course
from django.contrib.auth.models import User, Group


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'user%03d' % n)
    password = factory.PostGenerationMethodCall('set_password', 'test')


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
