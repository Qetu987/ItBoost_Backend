from django.urls import path
from education.views import (
    DashboardView, 
    ScheduleView, 
    TodayLessonScheduleView, 
    LessonThemeView, 
    AttendanceUserCheckView,
    AttendanceMarkCheckView
    )

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='DashboardView'),
    path('schedule/', ScheduleView.as_view(), name='ScheduleView'),
    path('today-schedule/', TodayLessonScheduleView.as_view(), name='today-schedule'),
    path('lessons/<int:lesson_id>/theme/', LessonThemeView.as_view(), name='lesson-theme'),
    path('lessons/<int:lesson_id>/check/<int:student_id>/', AttendanceUserCheckView.as_view(), name='attendance-user-check'),
    path('lessons/<int:lesson_id>/mark/<int:student_id>/', AttendanceMarkCheckView.as_view(), name='attendance-mark')
]