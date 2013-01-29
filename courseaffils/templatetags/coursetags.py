from django import template
from djangohelpers.templatetags import TemplateTagNode
from courseaffils.lib import get_public_name

register = template.Library()


class GetCourses(TemplateTagNode):
    noun_for = {"for": "user"}

    def __init__(self, varname, user):
        TemplateTagNode.__init__(self, varname, user=user)

    def execute_query(self, user):
        #import here, because it doesn't work above
        from courseaffils.models import Course
        return Course.objects.filter(group__in=user.groups.all())

register.tag('get_courses', GetCourses.process_tag)


class CourseRole(TemplateTagNode):
    noun_for = {"for": "user", "in": "course"}

    def __init__(self, varname, user, course):
        TemplateTagNode.__init__(self, varname, user=user, course=course)

    def execute_query(self, user, course):
        if not course:
            return "no-course"
        if not user in course.members:
            return "non-member"
        elif user in course.faculty:
            return "instructor"
        else:
            return "student"

register.tag('course_role', CourseRole.process_tag)


class PublicName(TemplateTagNode):
    noun_for = {"for": "user"}  # unnecessary, but here for documentation

    def __init__(self, varname, user, truncate=None):
        self.truncate = truncate
        TemplateTagNode.__init__(self, varname, user=user)

    def render(self, context):
        user_s = self.vars['user'].resolve(context)
        if self.truncate is not None:
            user_s = user_s[:self.truncate]
        return get_public_name(user_s, context['request'])

    @classmethod
    def process_tag(cls, parser, token):
        "words = (<tagname>,'for',<varname> [truncate <max_users>])"
        words = token.split_contents()
        if len(words) < 4:
            return cls(words[2], user=words[2])
        else:
            return cls(words[2], user=words[2], truncate=int(words[4]))
register.tag('public_name', PublicName.process_tag)

if not hasattr(template.defaulttags, 'csrf_token'):
    ### for Django1.1.2- compatibility
    @register.tag(name="csrf_token")
    def csrf_token(parser, token):
        return template.Node()
