import courseaffils.listener
# we need to make sure that the registration code
# gets imported, so we import it from models.py
# which will definitely be imported if the app
# is installed.

from django.db import models
from django.contrib.auth.models import Group

class Course(models.Model):
    group = models.OneToOneField(Group)
    title = models.CharField(max_length=1024)
    faculty_group = models.ForeignKey(Group,
                                      null=True,
                                      blank=True,
                                      related_name='faculty_of')

    def __unicode__(self):
        return self.title

    @property
    def members(self):
        return self.group.user_set.all()

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
        return self.group.user_set

    @property
    def faculty_filter(self):
        return reduce(lambda x,y:x|y, #composable Q's
                      [models.Q(author=f) for f in self.faculty],
                      models.Q(author= -1)#impossible
                      ) & models.Q(course=self)
        
        
    def is_faculty(self,user):
        return (user.is_staff or user in self.faculty)
    
