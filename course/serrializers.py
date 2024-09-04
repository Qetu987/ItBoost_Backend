from rest_framework import serializers
from course.models import Course, CourseMatherial


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'desc', 'Lesson_count', 'poster']


class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseMatherial
        fields = ['id', 'title', 'desc', 'pdf_file', 'date_create']

class CourseListSerializer(serializers.ModelSerializer):
    materials = CourseMaterialSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'desc', 'poster', 'date_create', 'Lesson_count', 'materials']