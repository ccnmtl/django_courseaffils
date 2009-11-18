from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.utils.http import urlquote
from django.conf import settings

from courseaffils.models import Course

import re

SESSION_KEY = 'ccnmtl.courseaffils.course'

def is_anonymous_path(current_path):
    if not hasattr(settings,'COURSEAFFILS_EXEMPT_PATHS'):
        return False

    for exempt_path in settings.COURSEAFFILS_EXEMPT_PATHS:
        try:
            if current_path.startswith(exempt_path):
                return True
        except TypeError: # it wasn't a string object .. must be a regex
            if exempt_path.match(current_path):
                return True

    return False
    

class CourseManagerMiddleware(object):
    def process_request(self, request):
        request.course = None #must be present to be a caching key

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
            request.course = course
            request.coursename = course.title
            request.actual_course_object = course

            if request.GET.has_key('next'):
                return HttpResponseRedirect(request.GET['next'])
            
            return None

        if request.session.has_key(SESSION_KEY):
            course = request.session[SESSION_KEY]
            request.course = course
            request.coursename = course.title
            request.actual_course_object = course
            return None

        available_courses = Course.objects.filter(group__user=request.user)

        if len(available_courses) == 1:
            request.session[SESSION_KEY] = course = \
                available_courses[0]
            request.course = course
            request.coursename = course.title
            request.actual_course_object = course
            return None

        if len(available_courses) == 0:
            return render_to_response('courseaffils/no_courses.html',
                                      {'request': request,
                                       'user': request.user,
                                       })

        next_redirect = ''
        if request.META.has_key('QUERY_STRING') \
               and not request.GET.has_key('unset_course') :
            #just GET (until someone complains)
            next_redirect = '&next=%s' % urlquote(request.get_full_path())
        return render_to_response('courseaffils/select_course.html',
                                  {
                'courses':available_courses,
                'user':request.user,
                'request': request,
                'next':next_redirect,
                },
                                  )

