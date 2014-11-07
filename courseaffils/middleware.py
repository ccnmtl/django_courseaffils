from django.http import HttpResponseRedirect
from django.conf import settings

from courseaffils.models import Course, CourseAccess
from courseaffils.views import select_course
from courseaffils.lib import AUTO_COURSE_SELECT
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import resolve, Resolver404

STRUCTURED_COLLABORATION_AVAILABLE = False
try:
    from structuredcollaboration.models import Collaboration
    STRUCTURED_COLLABORATION_AVAILABLE = True
except ImportError:
    pass

SESSION_KEY = 'ccnmtl.courseaffils.course'


def is_anonymous_path(current_path):
    if hasattr(settings, "ANONYMOUS_PATHS"):
        for path in settings.ANONYMOUS_PATHS:
            if isinstance(path, str):
                if current_path.startswith(path):
                    return True

    if hasattr(settings, 'COURSEAFFILS_PATHS'):
        for path in settings.COURSEAFFILS_PATHS:
            if isinstance(path, str):
                if current_path.startswith(path):
                    return False
            elif hasattr(path, 'match'):
                #regex
                if path.match(current_path):
                    return False

    if not hasattr(settings, 'COURSEAFFILS_EXEMPT_PATHS'):
        return False

    for exempt_path in settings.COURSEAFFILS_EXEMPT_PATHS:
        try:
            if current_path.startswith(exempt_path):
                return True
        except TypeError:  # it wasn't a string object .. must be a regex
            if exempt_path.match(current_path):
                return True

    # if whitelist, then default is to anonymous path
    return hasattr(settings, 'COURSEAFFILS_PATHS')


def already_selected_course(request):
    return SESSION_KEY in request.session


class CourseManagerMiddleware(object):
    def process_response(self, request, response):
        if 'ANONYMIZE' in request.COOKIES:
            for user, uid in getattr(request, 'scrub_names', {}).items():
                if len(user.last_name) > 3:
                    response.content = unicode(
                        response.content,
                        errors='ignore').replace(
                            user.get_full_name(), u'User Name_%d' % uid)
        return response

    def process_request(self, request):
        request.course = None  # must be present to be a caching key

        if is_anonymous_path(request.path):
            return None

        if (not request.user.is_authenticated()
                and not CourseAccess.allowed(request)):
            return None

        if 'unset_course' in request.GET:
            if SESSION_KEY in request.session:
                del request.session[SESSION_KEY]

        def decorate_request(request, course):
            request.course = course
            request.coursename = course.title

            # these will show up in Error emails as part of WSGI object
            request.environ['django_username'] = request.user.username
            request.environ['django_course'] = course.title

            if STRUCTURED_COLLABORATION_AVAILABLE:
                (request.collaboration_context,
                    created) = Collaboration.objects.get_or_create(
                        content_type=ContentType.objects.get_for_model(Course),
                        object_pk=str(course.pk))
                if created or request.collaboration_context.slug is None:
                    request.collaboration_context.title = course.title
                    request.collaboration_context.group = course.group

                    for i in range(2):
                        slug_try = course.slug(attempt=i)
                        if Collaboration.objects.filter(
                                slug=slug_try).count() == 0:
                            request.collaboration_context.slug = slug_try
                            break
                    request.collaboration_context.save()

        if 'set_course' in request.REQUEST:
            course = Course.objects.get(
                group__name=request.REQUEST['set_course'])
            if (request.user.is_staff
                    or CourseAccess.allowed(request)
                    or (request.user in course.members)):
                request.session[SESSION_KEY] = course
                decorate_request(request, course)

                if 'next' in request.GET:
                    return HttpResponseRedirect(request.GET['next'])

                return None

        if SESSION_KEY in request.session:
            course = request.session[SESSION_KEY]
            decorate_request(request, course)
            return None

        available_courses = Course.objects.filter(group__user=request.user)
        chosen_course = None
        try:
            requested_view, view_args, view_kwargs = resolve(
                request.get_full_path())
        except Resolver404:
            requested_view = None

        #staff should always get the opportunity to pick a course
        if requested_view in AUTO_COURSE_SELECT:
            chosen_course = AUTO_COURSE_SELECT[requested_view](
                *view_args, **view_kwargs)
        elif len(available_courses) == 1 and not request.user.is_staff:
            chosen_course = available_courses[0]

        if (chosen_course
                and (chosen_course in available_courses
                     or request.user.is_staff)):
            request.session[SESSION_KEY] = chosen_course
            decorate_request(request, chosen_course)
            return None

        return select_course(request)
