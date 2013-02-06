from django.db.models.loading import get_model
from django.template.loader import get_template
from django.template import Context
from django.http import Http404

User = get_model('auth', 'User')


def users_in_course(course):
    return User.objects.filter(groups=course.group)


def in_course(user, group_or_course):
    group = getattr(group_or_course, 'group', group_or_course)
    try:
        return group.user_set.get(username=user)
    except:
        return False


def in_course_or_404(user, group_or_course):
    "Supports either the course-group or course as second arg"
    group = getattr(group_or_course, 'group', group_or_course)
    try:
        return group.user_set.get(username=user)
    except:
        template = get_template('not_in_course.html')
        context = Context(
            {
                'user': user,
                'course': group,
            })
        response_body = template.render(context)
        raise Http404(response_body)

ANONYMIZE_KEY = 'ccnmtl.courseaffils.anonymize'


def handle_public_name(user, request):
    """guarantees no double-quotes so also json-friendly"""
    if 'ANONYMIZE' in request.COOKIES:
        request.__dict__.setdefault('scrub_names', {})
        request.scrub_names[user] = user.id
        return 'User Name_%d' % user.id
    else:
        return (user.get_full_name() or user.username).replace('"', "'")


def get_public_name(user_s, request):
    if hasattr(user_s, 'is_anonymous'):
        return handle_public_name(user_s, request)
    else:
        #for attribution lists, and such
        return ', '.join([handle_public_name(u, request) for u in user_s])

# AUTO_COURSE_SELECT is a dictionary that can be populated by other
# django apps in their views.py.  The KEY should be the view
# and the VALUE should be a function that takes the same arguments
# (except request) as the view, but returns the corresponding course
# If no course is possible it should return None
# SAMPLE VIEW CODE:
# from courseaffils.lib import AUTO_COURSE_SELECT
# def my_view(request, obj_id):
#    ....
# def my_view_courselookup(obj_id=None):
#    if obj_id:
#        return My.objects.get(pk=obj_id).course
# AUTO_COURSE_SELECT[my_view] = my_view_courselookup
#
AUTO_COURSE_SELECT = {}
