import json
from courseaffils.lib import get_current_term
from courseaffils.models import Course, CourseAccess
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list import ListView
from django.utils import timezone
from django.utils.http import urlquote
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth.models import User
from django.template import RequestContext


SESSION_KEY = 'ccnmtl.courseaffils.course'


def get_courses_for_user(user):
    courses = Course.objects.none()
    if user.is_staff:
        courses = Course.objects.all()
    elif not user.is_anonymous():
        courses = Course.objects.filter(group__user=user)
    return courses.order_by('-info__year', '-info__term', 'title')


def filter_past_courses(all_courses, current_term, current_year):
    """
    Given a queryset of courses, return only the ones in past
    semesters.
    """
    return all_courses.filter(
        Q(info__year__lt=current_year) |
        (Q(info__year=current_year) & Q(info__term__lt=current_term)))


def filter_current_courses(all_courses, current_term, current_year):
    """
    Given a queryset of courses, return only the ones in the
    current semester.
    """
    return all_courses.filter(
        info__year=current_year,
        info__term=current_term)


def filter_future_courses(all_courses, current_term, current_year):
    """
    Given a queryset of courses, return only the ones in
    future semesters.
    """
    return all_courses.filter(
        Q(info__year__gt=current_year) |
        (Q(info__year=current_year) & Q(info__term__gt=current_term)))


class CourseListView(ListView):
    model = Course

    def get_queryset(self):
        courses = get_courses_for_user(self.request.user)
        semester_view = self.request.GET.get('semester_view')
        current_term = get_current_term()
        current_year = timezone.now().year

        if semester_view == 'past':
            qs = filter_past_courses(courses, current_term, current_year)
        elif semester_view == 'future':
            qs = filter_future_courses(courses, current_term, current_year)
        else:
            qs = filter_current_courses(courses, current_term, current_year)
        return qs

    def get_context_data(self, **kwargs):
        context = super(CourseListView, self).get_context_data(**kwargs)
        semester_view = self.request.GET.get('semester_view', 'current')

        # If semester_view isn't future or past, always fall back to
        # current.
        if semester_view != 'future' and semester_view != 'past':
            semester_view = 'current'

        # infoless_courses don't have an associated CourseInfo. These
        # are our test courses, only visible to staff.
        infoless_courses = Course.objects.none()
        if self.request.user.is_staff:
            infoless_courses = Course.objects.filter(
                Q(info=None) | Q(info__term=None) | Q(info__year=None)
            ).order_by('title')

        next_redirect = ''
        if 'QUERY_STRING' in self.request.META \
           and 'unset_course' not in self.request.GET:
            # just GET (until someone complains)
            escaped_path = urlquote(self.request.get_full_path())
            next_redirect = '&next=' + escaped_path

        context.update({
            'add_privilege': self.request.user.is_staff,
            'semester_view': semester_view,
            'infoless_courses': infoless_courses,
            'next_redirect': next_redirect,
        })
        return context


def select_course(request):
    available_courses = get_courses_for_user(request.user)

    list_all_link = True
    if 'list_all' not in request.GET:
        current_year = timezone.now().year
        available_courses = available_courses.exclude(
            info__year__lt=current_year)
        list_all_link = False

    current_courses = filter_current_courses(available_courses)

    response_dict = {
        'request': request,
        'user': request.user,
        'add_privilege': request.user.is_staff,
        'current_courses': current_courses,
        'courses': available_courses,
        'list_all_link': list_all_link,
    }

    if len(available_courses) == 0 and not request.user.is_staff:
        return render_to_response('courseaffils/no_courses.html',
                                  response_dict)

    response_dict['next_redirect'] = ''
    if 'QUERY_STRING' in request.META \
            and 'unset_course' not in request.GET:
            # just GET (until someone complains)
        response_dict['next_redirect'] = '&next=%s' % (
            urlquote(request.get_full_path()))

    return render_to_response('courseaffils/select_course.html',
                              response_dict,
                              context_instance=RequestContext(request))


def course_list_query(request):
    if not CourseAccess.allowed(request):
        return HttpResponseForbidden('{"error":"server not whitelisted"}')
    user = get_object_or_404(
        User, username=request.REQUEST.get('user', 'none'))
    courses = get_courses_for_user(user)
    data = {'courses': dict(
            [(c.group.name, {'title': c.title, })
             for c in courses]
            )}
    return HttpResponse(
        json.dumps(data, indent=2),
        content_type='application/json')
