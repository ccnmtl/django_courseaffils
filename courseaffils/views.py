from django.conf import settings
from django.shortcuts import render_to_response
from courseaffils.models import Course
from django.db.models import get_model
from django.utils.http import urlquote

def select_course(request):
    available_courses = Course.objects.filter(group__user=request.user)
    response_dict = {'request': request,
                     'user': request.user,
                     'add_privilege':request.user.is_staff,
                     }

    if len(available_courses) == 0:
        return render_to_response('courseaffils/no_courses.html',
                                  response_dict)

    next_redirect = ''
    if request.META.has_key('QUERY_STRING') \
            and not request.GET.has_key('unset_course') :
            #just GET (until someone complains)
        next_redirect = '&next=%s' % urlquote(request.get_full_path())

    response_dict.update({
            'courses':available_courses,
            'next':next_redirect,
            'add_privilege':request.user.is_staff,
            })

    return render_to_response('courseaffils/select_course.html',
                              response_dict)

from django.http import HttpResponse
import simplejson
SESSION_KEY = 'ccnmtl.courseaffils.course'

def is_logged_in(request):
    """This could be a privacy hole, but since it's just logged in status, 
     it seems pretty harmless"""
    logged_in = request.user.is_authenticated()
    course_selected = request.session.has_key(SESSION_KEY)
    data = {
        "logged_in":logged_in,
        "course_selected":course_selected,
        "ready":(logged_in and course_selected),
        }
    jscript = """if (window.SherdBookmarklet) {
                  window.SherdBookmarklet.user_status = %s;
              }""" % simplejson.dumps(data)
    return HttpResponse(jscript,
                        mimetype='application/javascript')
    


def refresh_and_close_window(request):
    pass
