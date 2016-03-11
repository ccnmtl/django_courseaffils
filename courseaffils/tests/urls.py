from django.conf.urls import url
from courseaffils import views


urlpatterns = [
    url(r'^select_course/$', views.select_course, name='select_course'),
]
