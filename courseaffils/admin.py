from django.contrib import admin
from courseaffils.models import Course,CourseSettings,CourseInfo
from courseaffils.forms import CourseAdminForm
        
class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm

admin.site.register(Course, CourseAdmin)
admin.site.register(CourseSettings)
admin.site.register(CourseInfo)
