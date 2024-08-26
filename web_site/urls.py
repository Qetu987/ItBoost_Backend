from django.urls import path
from web_site.views import (
    CallBackRequestCreateView
    )

urlpatterns = [
    path('call_back_create/', CallBackRequestCreateView.as_view(), name='call_back_request_create_view'),
]