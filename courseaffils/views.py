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
