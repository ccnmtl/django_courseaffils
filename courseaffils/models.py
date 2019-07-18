from __future__ import unicode_literals

# we need to make sure that the registration code
# gets imported, so we import it from models.py
# which will definitely be imported if the app
# is installed.

from functools import reduce
from django.db import models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
import re
from django.conf import settings
from courseaffils.utils import get_current_term


@python_2_unicode_compatible
class Course(models.Model):
    is_course = True
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    title = models.CharField(max_length=1024)
    faculty_group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='faculty_of')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

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
        return re.sub(r'\W', '', re.sub(' ', '_', self.title))

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
        CourseDetails.objects.update_or_create(
            course=self, name=name, defaults={'value': value})


@python_2_unicode_compatible
class CourseSettings(models.Model):
    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name='settings')
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


@python_2_unicode_compatible
class CourseInfo(models.Model):
    term_choices = {1: 'Spring', 2: 'Summer', 3: 'Fall'}

    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name='info')

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
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
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
        secret = request.POST.get('secret', request.GET.get('secret', None))
        return (secret
                in getattr(settings, 'SERVER_ADMIN_SECRETKEYS', {}).values()
                )

    @classmethod
    def respond(cls, message):
        pass


@python_2_unicode_compatible
class Affil(models.Model):
    """Model for storing activatable affiliations.

    Faculty use this to 'activate' it into a Group/Course.
    """
    class Meta:
        unique_together = ('name', 'user')

    is_affil = True
    activated = models.BooleanField(default=False)
    name = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def to_dict(self):
        if hasattr(settings, 'COURSEAFFILS_COURSESTRING_MAPPER'):
            return settings.COURSEAFFILS_COURSESTRING_MAPPER.to_dict(
                self.name)
        else:
            return None

    @property
    def is_faculty(self):
        """Returns True if this affil is a faculty affil."""
        d = self.to_dict()
        return d.get('member') == 'fc'

    @property
    def past_present_future(self):
        """Find out if this Affil is in the past, present, or future.

        Returns -1 if this Affil is in the past, 0 if in the present,
        and 1 if in the future. If there was a parse error, returns None.
        """
        current_year = timezone.now().year
        current_term = get_current_term()

        affil_dict = self.to_dict()

        if affil_dict is None:
            return None

        try:
            year = int(affil_dict.get('year'))
        except TypeError:
            return None

        try:
            term = int(affil_dict.get('term'))
        except TypeError:
            return None

        if year == current_year and term == current_term:
            return 0
        elif year < current_year or (
                year == current_year and term < current_term):
            return -1
        else:
            return 1

    @property
    def courseworks_name(self):
        """Returns the Courseworks formatted name.

        e.g.: CUcourse_NURSN6610_001_2008_2

        If no mapper is configured, returns None.
        """
        if hasattr(settings, 'COURSEAFFILS_COURSESTRING_MAPPER') and \
           settings.COURSEAFFILS_COURSESTRING_MAPPER is not None:
            affil_dict = self.to_dict()
            return 'CUcourse_{}{}{}_{}_{}_{}'.format(
                affil_dict['dept'].upper(),
                affil_dict['letter'],
                affil_dict['number'],
                affil_dict['section'],
                affil_dict['year'],
                affil_dict['term'])
        return None

    @property
    def coursedirectory_name(self):
        """Returns the Course Directory formatted name.

        e.g.: 20082NURS6610N001

        If no mapper is configured, returns None.
        """
        if hasattr(settings, 'COURSEAFFILS_COURSESTRING_MAPPER') and \
           settings.COURSEAFFILS_COURSESTRING_MAPPER is not None:
            affil_dict = self.to_dict()
            return '{}{}{}{}{}{}'.format(
                affil_dict['year'],
                affil_dict['term'],
                affil_dict['dept'].upper(),
                affil_dict['number'],
                affil_dict['letter'].upper(),
                affil_dict['section'])
        return None

    @property
    def shortname(self):
        affil_dict = self.to_dict()
        if affil_dict is not None:
            return affil_dict['dept'].upper() + affil_dict['number']

    def get_course(self):
        """Returns an associated course for this affil, if it exists."""
        fgroup = Group.objects.filter(name=self.name).first()
        if Course.objects.filter(faculty_group=fgroup).exists():
            return Course.objects.filter(faculty_group=fgroup).first()

        studentaffil = re.sub(r'\.fc\.', '.st.', self.name)
        sgroup = Group.objects.filter(name=studentaffil).first()
        if Course.objects.filter(group=sgroup).exists():
            return Course.objects.filter(group=sgroup).first()

        return None
