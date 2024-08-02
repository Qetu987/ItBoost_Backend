from django.urls import path
from education.views import DashboardView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='DashboardView'),
]