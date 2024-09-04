from django.urls import path
from course.views import (
    CourseMaterialView
    )

urlpatterns = [
    path('courses-materials/', CourseMaterialView.as_view(), name='courses-materials'),
]