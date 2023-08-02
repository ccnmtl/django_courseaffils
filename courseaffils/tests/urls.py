from __future__ import unicode_literals

from django.urls import path
from courseaffils import views


urlpatterns = [
    path('select_course/',
         views.CourseListView.as_view(),
         name='select_course'),
    path('course/create/',
         views.CourseCreateView.as_view(),
         name='create_course'),
]
