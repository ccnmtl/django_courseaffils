from __future__ import unicode_literals

from django import template
from courseaffils.lib import get_public_name
from courseaffils.views import get_courses_for_instructor

register = template.Library()


def chunk(chunkable, size=2):
    chunkable = list(chunkable)
    chunked = []
    sublist = []
    while len(chunkable):
        for i in range(size):
            sublist.append(chunkable.pop(0))
        chunked.append(sublist)
        sublist = []
    return chunked


class TemplateTagNode(template.Node):

    noun_for = {'by': 'who'}

    @classmethod
    def error_msg(cls):
        parts = []
        for preposition, noun in cls.noun_for.items():
            parts.append("%s <%s>" % (preposition, noun))
        parts = ' '.join(parts)

        msg = """Invalid tag syntax "%s"
Syntax: %s """ + parts + """ as <varname>"""
        return msg

    @classmethod
    def process_tag(cls, parser, token):
        words = token.split_contents()
        tag_name, words = words[0], words[1:]

        _as, varname = words[-2:]
        words = words[:-2]

        if _as != 'as':
            raise (
                template.TemplateSyntaxError,
                cls.error_msg() % (token.contents, tag_name))

        words = chunk(words)
        if len(words) != len(cls.noun_for):
            raise (
                template.TemplateSyntaxError,
                cls.error_msg() % (token.contents, tag_name))

        kw = {}
        for phrase in words:
            preposition, noun = phrase
            if preposition not in cls.noun_for \
                    or cls.noun_for[preposition] in kw:
                raise (
                    template.TemplateSyntaxError,
                    cls.error_msg() % (token.contents, tag_name))
            kw[cls.noun_for[preposition]] = noun

        return cls(varname, **kw)

    def __init__(self, varname, **kw):
        self.varname = varname
        self.vars = {}
        for key, var in kw.items():
            self.vars[key] = template.Variable(var)

    def render(self, context):
        vars = dict(self.vars)
        for key, var in vars.items():
            vars[key] = var.resolve(context)

        context[self.varname] = self.execute_query(**vars)
        return ''

    def execute_query(self, **kw):
        return ''


class GetCourses(TemplateTagNode):
    noun_for = {"for": "user"}

    def __init__(self, varname, user):
        TemplateTagNode.__init__(self, varname, user=user)

    def execute_query(self, user):
        from courseaffils.views import get_courses_for_user
        return get_courses_for_user(user)


register.tag('get_courses', GetCourses.process_tag)


@register.simple_tag
def get_instructor_courses(user):
    return get_courses_for_instructor(user)


class CourseRole(TemplateTagNode):
    noun_for = {"for": "user", "in": "course"}

    def __init__(self, varname, user, course):
        TemplateTagNode.__init__(self, varname, user=user, course=course)

    def execute_query(self, user, course):
        if not course:
            return "no-course"
        elif course.is_true_faculty(user):
            return "instructor"
        elif course.is_true_member(user):
            return "student"
        else:
            return "non-member"


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
