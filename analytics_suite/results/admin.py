from django.contrib import admin
from .models import Student, Course, ResultRecord

admin.site.register(Student)
admin.site.register(Course)
admin.site.register(ResultRecord)