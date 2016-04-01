from __future__ import unicode_literals

from django.conf.urls import url
from courseaffils import views


urlpatterns = [
    url(r'^select_course/$',
        views.CourseListView.as_view(),
        name='select_course'),
    url(r'^course/create/$',
        views.CourseCreateView.as_view(),
        name='create_course'),
]
