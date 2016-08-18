from __future__ import unicode_literals

from django.contrib import admin
from courseaffils.models import (
    Affil,
    Course, CourseSettings, CourseInfo, CourseDetails
)
from courseaffils.forms import CourseAdminForm


class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm

    search_fields = ('title',)
    list_display = ('title', 'id',)
    change_form_template = "courseaffils/admin_change_form.html"


class AffilAdmin(admin.ModelAdmin):
    model = Affil
    list_display = ['name', 'user']


admin.site.register(Course, CourseAdmin)
admin.site.register(Affil, AffilAdmin)
admin.site.register(CourseSettings)
admin.site.register(CourseInfo)
admin.site.register(CourseDetails)
