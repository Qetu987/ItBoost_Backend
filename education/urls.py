from django.urls import path
from education.views import (
    DashboardView, 
    ScheduleView, 
    TodayLessonScheduleView, 
    LessonThemeView, 
    AttendanceUserCheckView,
    AttendanceMarkCheckView,
    HomeworksSetView,
    HomeworksToCheckView,
    SubmissionSetView,
    SubmissionSetMarkView,
    StudentHomeworksByCourseView,
    TeacherSubmissionsByGroupView,
    )

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='DashboardView'),
    path('schedule/', ScheduleView.as_view(), name='ScheduleView'),
    path('today-schedule/', TodayLessonScheduleView.as_view(), name='today-schedule'),
    path('lessons/<int:lesson_id>/theme/', LessonThemeView.as_view(), name='lesson-theme'),
    path('lessons/<int:lesson_id>/check/<int:student_id>/', AttendanceUserCheckView.as_view(), name='attendance-user-check'),
    path('lessons/<int:lesson_id>/mark/<int:student_id>/', AttendanceMarkCheckView.as_view(), name='attendance-mark'),
    path('homework/set/', HomeworksSetView.as_view(), name='homework-set'),
    path('homework/to_check/', HomeworksToCheckView.as_view(), name='homework-to-check'),
    path('homework/all_students_homeworks/', StudentHomeworksByCourseView.as_view(), name='all-students-homeworks'),
    path('homework/all_teachers_homeworks/', TeacherSubmissionsByGroupView.as_view(), name='all-teachers-homeworks'),

    path('submission/to_send/', SubmissionSetView.as_view(), name='submission-to-send'),
    path('submission/set_mark/', SubmissionSetMarkView.as_view(), name='submission-set-mark'),
]