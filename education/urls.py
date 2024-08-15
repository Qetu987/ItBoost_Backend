from django.urls import path
from education.views import DashboardView, ScheduleView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='DashboardView'),
    path('schedule/', ScheduleView.as_view(), name='ScheduleView'),
]