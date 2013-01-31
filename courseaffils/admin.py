from django.contrib import admin
from courseaffils.models import Course, CourseSettings
from courseaffils.models import CourseInfo, CourseDetails
from courseaffils.forms import CourseAdminForm


class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm

    search_fields = ('title', 'group__name',
                     'faculty_group__user__last_name')
    list_display = ('title', 'id',)
    change_form_template = "courseaffils/admin_change_form.html"

admin.site.register(Course, CourseAdmin)
admin.site.register(CourseSettings)
admin.site.register(CourseInfo)
admin.site.register(CourseDetails)
