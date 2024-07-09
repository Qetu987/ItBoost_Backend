from django.contrib import admin
from course.models import Course, CourseMatherial
from django.utils.safestring import mark_safe

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'date_create', 'get_image', 'owner', 'is_active', 'Lesson_count']
    list_display_links = ['id', 'title', 'owner']
    list_search = ['id', 'title']
    list_filter = ['owner', 'is_active', 'Lesson_count']

    def get_image(self, obj):
        try:
            a = mark_safe(f'<img src={obj.poster.url} width="100" height="110">')
        except:
            a = None
        return a
    get_image.short_description = "Image"


@admin.register(CourseMatherial)
class CourseMatherialAdmin(admin.ModelAdmin):
    list_display = ['id', 'course', 'title', 'owner', 'date_create']
    list_display_links = ['id', 'course', 'title', 'owner']
    list_search = ['id', 'course', 'title']
    list_filter = ['owner', 'course']