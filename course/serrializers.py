from rest_framework import serializers
from course.models import Course


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'desc', 'Lesson_count', 'poster']