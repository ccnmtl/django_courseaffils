from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.utils.http import urlquote
from django.conf import settings

from courseaffils.models import Course
from courseaffils.views import select_course
from courseaffils.lib import AUTO_COURSE_SELECT
from django.db.models import get_model
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse,resolve,Resolver404        

Collaboration = get_model('structuredcollaboration','collaboration')

import re

SESSION_KEY = 'ccnmtl.courseaffils.course'

def is_anonymous_path(current_path):
    if hasattr(settings,'COURSEAFFILS_PATHS'):
        for path in settings.COURSEAFFILS_PATHS:
            if isinstance(path,str):
                if current_path.startswith(path):
                    return False
            elif hasattr(path,'match'):
                #regex
                if path.match(current_path):
                    return False

    if not hasattr(settings,'COURSEAFFILS_EXEMPT_PATHS'):
        return False

    for exempt_path in settings.COURSEAFFILS_EXEMPT_PATHS:
        try:
            if current_path.startswith(exempt_path):
                return True
        except TypeError: # it wasn't a string object .. must be a regex
            if exempt_path.match(current_path):
                return True

    #if whitelist, then default is to anonymous path
    return hasattr(settings,'COURSEAFFILS_PATHS')
    

def already_selected_course(request):
    return request.session.has_key(SESSION_KEY)

class CourseManagerMiddleware(object):
    def process_request(self, request):
        request.course = None #must be present to be a caching key

        path = urlquote(request.get_full_path())
        if is_anonymous_path(request.path):
            return None

        if not request.user.is_authenticated():
            return None

        if request.GET.has_key('unset_course'):
            if request.session.has_key(SESSION_KEY):
                del request.session[SESSION_KEY]

        def decorate_request(request,course):
            request.course = course
            request.coursename = course.title

            if Collaboration: #if structuredcollaboration app is installed
                request.collaboration_context,created = Collaboration.objects.get_or_create(
                    content_type=ContentType.objects.get_for_model(Course),
                    object_pk=str(course.pk),
                    group=course.group,
                    )
                if created or request.collaboration_context.slug is None:
                    request.collaboration_context.title = course.title
                    request.collaboration_context.slug = course.slug
                    request.collaboration_context.save()

        if request.GET.has_key('set_course'):
            course = Course.objects.get(group__name=request.GET['set_course'])
            if request.user.is_staff or (request.user in course.members):
                request.session[SESSION_KEY] = course
                decorate_request(request,course)

                if request.GET.has_key('next'):
                    return HttpResponseRedirect(request.GET['next'])
            
                return None

        if request.session.has_key(SESSION_KEY):
            course = request.session[SESSION_KEY]
            decorate_request(request,course)
            return None

        available_courses = Course.objects.filter(group__user=request.user)
        chosen_course = None
        try:
            requested_view,view_args,view_kwargs = resolve(request.get_full_path())
        except Resolver404:
            requested_view = None

        if len(available_courses) == 1:
            chosen_course = available_courses[0]
        elif AUTO_COURSE_SELECT.has_key(requested_view):
            chosen_course = AUTO_COURSE_SELECT[requested_view](*view_args, **view_kwargs)

        if chosen_course and chosen_course in available_courses:
            request.session[SESSION_KEY] = chosen_course
            decorate_request(request,chosen_course)
            return None

        return select_course(request)

