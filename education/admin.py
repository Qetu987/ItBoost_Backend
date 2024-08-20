from django.contrib import admin
from education.models import Group, Lesson, Homework, Submission, Attendance, LessonGrade
from django.utils.safestring import mark_safe

@admin.register(Group)
class GrouplAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'get_image', 'date_create', 'owner']
    list_display_links = ['id', 'title', 'owner']
    list_search = ['id', 'owner', 'title']
    list_filter = ['owner']
    
    def get_image(self, obj):
        try:
            a = mark_safe(f'<img src={obj.poster.url} width="100" height="110">')
        except:
            a = None
        return a
    get_image.short_description = "Image"


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['id', 'course', 'title', 'date_create', 'teacher', 'group']
    list_display_links = ['id', 'course', 'title', 'teacher']
    list_search = ['id', 'course', 'title', 'teacher', 'group']
    list_filter = ['course', 'teacher', 'group']


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ['id', 'lesson', 'title', 'due_date', 'date_create']
    list_display_links = ['id', 'lesson', 'title', 'due_date', 'date_create']
    list_search = ['id', 'lesson', 'title', 'due_date', 'date_create']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'homework', 'student', 'date_submitted', 'grade', 'comment']
    list_display_links = ['id', 'homework', 'student', 'date_submitted', 'grade']
    list_search = ['id', 'homework', 'student', 'grade', 'date_submitted']
    list_filter = ['grade']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['id', 'lesson', 'student', 'is_present', 'date']
    list_display_links = ['id', 'lesson', 'student', 'is_present', 'date']
    list_search = ['id', 'lesson', 'student', 'date']
    list_filter = ['is_present']


@admin.register(LessonGrade)
class LessonGradeAdmin(admin.ModelAdmin):
    list_display = ['id', 'lesson', 'student', 'grade', 'date']
    list_display_links = ['id', 'lesson', 'student', 'grade', 'date']
    list_search = ['id', 'lesson', 'student', 'date']
    list_filter = ['grade']