from django.contrib import admin
from courseaffils.models import Course
from courseaffils.forms import CourseAdminForm
        
class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm

admin.site.register(Course, CourseAdmin)
