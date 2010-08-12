import courseaffils.listener
# we need to make sure that the registration code
# gets imported, so we import it from models.py
# which will definitely be imported if the app
# is installed.

from django.db import models
from django.contrib.auth.models import Group
import re
from django.conf import settings

class Course(models.Model):
    group = models.OneToOneField(Group)
    title = models.CharField(max_length=1024)
    faculty_group = models.ForeignKey(Group,
                                      null=True,
                                      blank=True,
                                      related_name='faculty_of')

    def __unicode__(self):
        return self.title

    def save(self, *args, **kw):
        new = (not self.pk)
        models.Model.save(self, *args, **kw)

        if new and hasattr(settings,'COURSEAFFILS_COURSESTRING_MAPPER'):
            if hasattr(settings.COURSEAFFILS_COURSESTRING_MAPPER,'on_create'):
                settings.COURSEAFFILS_COURSESTRING_MAPPER.on_create(self)
            

    @property
    def members(self):
        return self.group.user_set.all().order_by('first_name','last_name','username')

    @property
    def students(self):
        members =  self.group.user_set.all()
        if not self.faculty_group:
            return members
        else:
            faculty = self.faculty_group.user_set.all()
            return [m for m in members if m not in faculty]

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
        return reduce(lambda x,y:x|y, #composable Q's
                      [models.Q(author=f) for f in self.faculty],
                      models.Q(author= -1)#impossible
                      ) & models.Q(course=self)
        
        
    def is_faculty(self,user):
        return (user.is_staff or user in self.faculty)
    
    def is_member(self,user):
        return (user.is_staff or user in self.members)
    
    @property
    def slug(self):
        course_string = re.match('t(\d).y(\d{4}).s(\d{3}).c(\w)(\d{4}).(\w{4})',self.group.name)
        if course_string:
            t,y,s,let,num,dept = course_string.groups()
            return '%s%s%s' % ('CU',dept,num)
        else:
            return re.sub('\W','',re.sub(' ','_',self.title))

    def details(self):
        return dict([(i.name,i) for i in CourseDetails.objects.filter(course=self)])

class CourseSettings(models.Model):
    course = models.OneToOneField(Course, related_name='settings')
    
    custom_headers = models.TextField(blank=True, null=True,
                                      help_text="""Replaces main.css link in header.  You need to add this as full HTML (&lt;link rel="stylesheet" href="...." />) but the advantage is you can add custom javascript here, too.""")
    
    def __unicode__(self):
        return u'Settings for %s' % self.course.title

class CourseInfo(models.Model):
    term_choices = {1:'Spring',2:'Summer',3:'Fall'}

    course = models.OneToOneField(Course, related_name='info')

    year = models.IntegerField(null=True, blank=True)
    term = models.IntegerField(null=True, blank=True, choices=term_choices.items() )

    #for ability to query what courses are going on NOW
    starttime = models.TimeField(null=True, blank=True)
    endtime = models.TimeField(null=True, blank=True)
    days = models.CharField(max_length=7,null=True, blank=True) #e.g. 'MWF'

    def termyear(self):
        return '%s %d' % (self.term_choices[self.term], self.year)

    def __unicode__(self):
        return u'%s (%s) %s %s-%s' % (self.course.title,
                                      self.termyear(),
                                      self.days,self.starttime,self.endtime)

class CourseDetails(models.Model):
    """useful for storing info like 'semester', 'url' """
    course = models.ForeignKey(Course)
    name = models.CharField(max_length=64)
    value = models.CharField(max_length=1024)

    def __unicode__(self):
        return u'(%s) %s: %s' % (self.course.title, self.name, self.value)

    class Meta:
        verbose_name_plural = 'Course Info'


    
#### Structured Collaboration Support ####
try:
    import policies
except ImportError:
    pass
