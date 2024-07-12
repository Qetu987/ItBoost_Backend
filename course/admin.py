from django.contrib import admin
from course.models import Course, CourseMatherial
from user.models import CustomUser
from django.utils.translation import gettext_lazy as _
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

class ModeratorFilter(admin.SimpleListFilter):
    title = _('Moderator')
    parameter_name = 'moderator'

    def lookups(self, request, model_admin):
        moderators = CustomUser.objects.filter(moderatorprofile__isnull=False)
        return [(moderator.id, moderator.username) for moderator in moderators]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(owner__user_id=self.value())
        return queryset

@admin.register(CourseMatherial)
class CourseMatherialAdmin(admin.ModelAdmin):
    list_display = ['id', 'course', 'title', 'owner', 'date_create']
    list_display_links = ['id', 'course', 'title', 'owner']
    list_search = ['id', 'course', 'title']
    list_filter = [ModeratorFilter, 'course']