from django.test import TestCase
from courseaffils.middleware import is_anonymous_path
from courseaffils.middleware import already_selected_course
from courseaffils.middleware import CourseManagerMiddleware
