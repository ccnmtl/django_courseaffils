import courseaffils.listener
# we need to make sure that the registration code
# gets imported, so we import it from models.py
# which will definitely be imported if the app
# is installed.

from django.db import models
from django.contrib.auth.models import Group

class Course(models.Model):
    group = models.ForeignKey(Group)
    title = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.title

    @property
    def students(self):
        #currently broken, because faculty will
        #also be included
        return self.group.user_set.all()
    
    @property
    def user_set(self):
        return self.group.user_set
