from django.db.models.loading import get_model

User = get_model('auth', 'User')

def users_in_course(course):
    return User.objects.filter(groups=course__group)

def in_course(user, course):
    return course.group in user.groups
