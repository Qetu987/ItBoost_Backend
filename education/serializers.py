from rest_framework import serializers
from education.models import Lesson
from user.models import CustomUser
from user.serializers import UserSerializer



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