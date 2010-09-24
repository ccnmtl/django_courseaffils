from django.contrib import admin
from courseaffils.models import Course,CourseSettings,CourseInfo,CourseDetails
from courseaffils.forms import CourseAdminForm
        
class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm
    
    change_form_template="courseaffils/admin_change_form.html"


admin.site.register(Course, CourseAdmin)
admin.site.register(CourseSettings)
admin.site.register(CourseInfo)
admin.site.register(CourseDetails)
