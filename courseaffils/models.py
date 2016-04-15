from __future__ import unicode_literals

# we need to make sure that the registration code
# gets imported, so we import it from models.py
# which will definitely be imported if the app
# is installed.

from functools import reduce
from django.db import models
from django.contrib.auth.models import Group
from django.utils.encoding import python_2_unicode_compatible
import re
from django.conf import settings


@python_2_unicode_compatible
class Course(models.Model):
    is_course = True
    group = models.OneToOneField(Group)
    title = models.CharField(max_length=1024)
    faculty_group = models.ForeignKey(Group,
                                      null=True,
                                      blank=True,
                                      related_name='faculty_of')

    def __str__(self):
        return self.title

    def save(self, *args, **kw):
        new = (not self.pk)
        models.Model.save(self, *args, **kw)

        if new and hasattr(settings, 'COURSEAFFILS_COURSESTRING_MAPPER'):
            if hasattr(settings.COURSEAFFILS_COURSESTRING_MAPPER, 'on_create'):
                settings.COURSEAFFILS_COURSESTRING_MAPPER.on_create(self)

    @property
    def members(self):
        return self.group.user_set.all().order_by(
            'first_name', 'last_name', 'username')

    @property
    def students(self):
        members = self.group.user_set.all()
        if not self.faculty_group:
            return members
        else:
            ids = self.faculty_group.user_set.values_list('id', flat=True)
            return members.exclude(id__in=ids)

    @property
    def faculty(self):
        if self.faculty_group:
            return self.faculty_group.user_set.all()
        else:
            return tuple()

    @property
    def user_set(self):
        if self.group_id:
            return self.group.user_set
        else:
            return None

    @property
    def faculty_filter(self):
        return reduce(lambda x, y: x | y,  # composable Q's
                      [models.Q(author=f) for f in self.faculty],
                      models.Q(author=-1)  # impossible
                      ) & models.Q(course=self)

    def is_faculty(self, user):
        return user.is_staff or (
            self.faculty_group and
            self.faculty_group.user_set.filter(id=user.id).exists())

    def is_member(self, user):
        return (user.is_staff or
                self.group.user_set.filter(id=user.id).exists())

    def is_true_member(self, user):
        return self.group.user_set.filter(id=user.id).exists()

    def is_true_faculty(self, user):
        return self.faculty_group and (
            self.faculty_group.user_set.filter(id=user.id).exists())

    def default_slug(self, **kw):
        return re.sub('\W', '', re.sub(' ', '_', self.title))

    def slug(self, **kw):
        if hasattr(settings, 'COURSEAFFILS_COURSESTRING_MAPPER'):
            if hasattr(settings.COURSEAFFILS_COURSESTRING_MAPPER,
                       'course_slug'):
                return settings.COURSEAFFILS_COURSESTRING_MAPPER.course_slug(
                    self, **kw)

        return self.default_slug(**kw)

    def details(self):
        return dict(
            [(i.name, i) for i in self.coursedetails_set.all()]
        )

    def get_detail(self, name, default):
        try:
            return CourseDetails.objects.get(course=self, name=name).value
        except CourseDetails.DoesNotExist:
            return default

    def add_detail(self, name, value):
        try:
            detail = CourseDetails.objects.get(course=self, name=name)
            detail.value = value
            detail.save()
        except CourseDetails.DoesNotExist:
            detail = CourseDetails.objects.create(
                course=self, name=name, value=value)


@python_2_unicode_compatible
class CourseSettings(models.Model):
    course = models.OneToOneField(Course, related_name='settings')
    custom_headers = models.TextField(
        blank=True, null=True,
        help_text=("""Replaces main.css link in header.  """
                   """You need to add this as full HTML (&lt;link """
                   """rel="stylesheet" href="...." />) but the """
                   """advantage is you can add custom javascript here, too.""")
    )

    def __str__(self):
        return 'Settings for %s' % self.course.title

    class Meta:
        verbose_name_plural = 'Course Settings'


class CourseInfo(models.Model):
    term_choices = {1: 'Spring', 2: 'Summer', 3: 'Fall'}

    course = models.OneToOneField(Course, related_name='info')

    year = models.IntegerField(null=True, blank=True)
    term = models.IntegerField(
        null=True, blank=True, choices=term_choices.items())

    # for ability to query what courses are going on NOW
    starttime = models.TimeField(null=True, blank=True)
    endtime = models.TimeField(null=True, blank=True)
    days = models.CharField(
        max_length=7, null=True, blank=True,
        help_text='e.g. "MTWRF"')

    def time(self):
        return '%s%s' % (
            self.days if self.days else '',
            ' %s-%s' % (self.starttime.strftime('%H:%M'),
                        self.endtime.strftime('%H:%M')
                        ) if self.starttime else ''
        )

    def termyear(self):
        term = self.term_choices.get(self.term, '')
        if self.year:
            term = term + (' %d' % self.year)
        return term

    def display(self):
        return '%s %s %s-%s' % (self.termyear(),
                                self.days, self.starttime, self.endtime)

    def __str__(self):
        return '%s (%s) %s %s-%s' % (self.course.title,
                                     self.termyear(),
                                     self.days, self.starttime, self.endtime)

    class Meta:
        verbose_name_plural = 'Course Info'


@python_2_unicode_compatible
class CourseDetails(models.Model):
    """useful for storing info like 'semester', 'url' """
    course = models.ForeignKey(Course)
    name = models.CharField(
        max_length=64,
        help_text=("""type of data. Useful ones are """
                   """'instructor', 'semester', 'url', """
                   """'campus', 'times', 'call_number'"""))
    value = models.CharField(max_length=1024,
                             help_text="""The name's value for the course.""")

    def __str__(self):
        return '(%s) %s: %s' % (self.course.title, self.name, self.value)

    class Meta:
        verbose_name_plural = 'Course Details'


# server2server admin access support
class CourseAccess:
    @classmethod
    def allowed(cls, request):
        return (request.REQUEST.get('secret', None)
                in getattr(settings, 'SERVER_ADMIN_SECRETKEYS', {}).values()
                )

    @classmethod
    def respond(cls, message):
        pass
