from django import template
from djangohelpers.templatetags import TemplateTagNode

from courseaffils.models import Course

register = template.Library()

class GetCourses(TemplateTagNode):
    noun_for = {"for": "user"}

    def __init__(self, varname, user):
        TemplateTagNode.__init__(self, varname, user=user)

    def execute_query(self, user):
        return Course.objects.filter(group__in=user.groups.all())

register.tag('get_courses', GetCourses.process_tag)
