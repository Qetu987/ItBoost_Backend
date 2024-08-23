from django.urls import path
from education.views import DashboardView, ScheduleView, TodayLessonScheduleView, LessonThemeView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='DashboardView'),
    path('schedule/', ScheduleView.as_view(), name='ScheduleView'),
    path('today-schedule/', TodayLessonScheduleView.as_view(), name='today-schedule'),
    path('today-schedule/<int:lesson_id>/', TodayLessonScheduleView.as_view(), name='specific-lesson-schedule'),
    path('lessons/<int:lesson_id>/theme/', LessonThemeView.as_view(), name='lesson-theme'),
]