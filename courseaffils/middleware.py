from django.shortcuts import render_to_response
from django.utils.http import urlquote
from django.conf import settings

from courseaffils.models import Course

import re

SESSION_KEY = 'ccnmtl.courseaffils.course'

def is_anonymous_path(path):
    if hasattr(settings,'ANONYMOUS_PATHS'):
        for allowed_prefix in settings.ANONYMOUS_PATHS:
            if hasattr(allowed_prefix,'match'):
                if allowed_prefix.match(path):
                    return True
            elif path.startswith(allowed_prefix):
                return True
    return False
    

class CourseManagerMiddleware(object):
    def process_request(self, request):
        path = urlquote(request.get_full_path())
        if is_anonymous_path(path):
            return None

        if not request.user.is_authenticated():
            return None

        if request.GET.has_key('unset_course'):
            if request.session.has_key(SESSION_KEY):
                del request.session[SESSION_KEY]

        if request.GET.has_key('set_course'):
            request.session[SESSION_KEY] = course = \
                Course.objects.get(group__name=request.GET['set_course'])
            request.course = course.group
            request.coursename = course.title
            request.actual_course_object = course
            return None

        if request.session.has_key(SESSION_KEY):
            course = request.session[SESSION_KEY]
            request.course = course.group
            request.coursename = course.title
            request.actual_course_object = course
            return None

        available_courses = Course.objects.filter(group__user=request.user)

        if len(available_courses) == 1:
            request.session[SESSION_KEY] = course = \
                available_courses[0]
            request.course = course.group
            request.coursename = course.title
            request.actual_course_object = course
            return None

        if len(available_courses) == 0:
            return render_to_response('courseaffils/no_courses.html',
                                      {'request': request,
                                       'user': request.user,
                                       })

        return render_to_response('courseaffils/select_course.html',
                                  {
                'courses':available_courses,
                'user':request.user,
                'request': request,
                },
                                  )

