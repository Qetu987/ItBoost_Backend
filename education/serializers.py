from rest_framework import serializers
from education.models import Lesson
from user.models import CustomUser
from user.serializers import UserSerializer, TeacherProfileSerializer
from course.serrializers import CourseSerializer



class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'pdf_material', 'video_url']

class CustomDataSerializer(serializers.Serializer):
    user = UserSerializer()
    homeworks = serializers.IntegerField()
    average_mark = serializers.FloatField()
    lesson_visited = serializers.DictField()
    future_lessons = LessonSerializer(many=True)


class LessonScheduleSerializer(serializers.ModelSerializer):
    teacher = TeacherProfileSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'title', 'description', 'pdf_material', 'video_url', 'date_create', 'lesson_date', 'teacher']

class ScheduleSerializer(serializers.Serializer):
    week = LessonScheduleSerializer(many=True)
    month = LessonScheduleSerializer(many=True)