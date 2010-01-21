from django.conf import settings
from django.shortcuts import render_to_response
from courseaffils.models import Course
from django.db.models import get_model


def select_course(request):
    available_courses = Course.objects.filter(group__user=request.user)
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


def get_mappers(self):
    mappers = []
    if not hasattr(settings,'COURSEAFFILS_FACULTY_GROUPS'):
        return []
    for mapper_path in settings.WIND_AFFIL_HANDLERS:
        mappers.append(self.load_handler(mapper_path))
    return mappers
