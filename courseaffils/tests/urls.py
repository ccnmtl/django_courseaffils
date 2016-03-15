from django.conf.urls import url
from courseaffils import views


urlpatterns = [
    url(r'^select_course/$',
        views.CourseListView.as_view(),
        name='select_course'),
]
