from django.db.models.loading import get_model
from django.template.loader import get_template
from django.template import Context
from django.http import Http404

User = get_model('auth', 'User')

def users_in_course(course):
    return User.objects.filter(groups=course.group)

def in_course(user, course):
    return course.group in user.groups

def in_course_or_404(user, group_or_course):
    "Supports either the course-group or course as second arg"
    group = getattr(group_or_course,'group', group_or_course)
    try:
        return group.user_set.get(username=user)
    except:
        template = get_template('not_in_course.html')
        context = Context({
                'user': user,
                'course': group,
                })
        response_body = template.render(context)
        raise Http404(response_body)
