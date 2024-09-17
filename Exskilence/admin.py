from django.contrib import admin

from .models import *

admin.site.register(login_data)
admin.site.register(StudentDetails)
admin.site.register(CourseDetails)
admin.site.register(InternshipDetails)
admin.site.register(QuestionDetails_Days)
admin.site.register(StudentDetails_Days_Questions)
admin.site.register(BugDetails)

admin.site.register(CoursePackages)
admin.site.register(StudentProfile)
admin.site.register(ContactInfo)
admin.site.register(Login)
admin.site.register(Switches)
