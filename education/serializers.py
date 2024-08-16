from rest_framework import serializers
from education.models import Lesson, Attendance
from user.models import StudentProfile
from user.serializers import UserSerializer, TeacherProfileSerializer
from course.serrializers import CourseSerializer
from django.utils import timezone



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
        fields = ['id', 'course', 'title', 'description', 'pdf_material', 'video_url', 'date_create', 'lesson_date', 'teacher', 'group']

class ScheduleSerializer(serializers.Serializer):
    week = LessonScheduleSerializer(many=True)
    month = LessonScheduleSerializer(many=True)

class AttendanceSerializer(serializers.ModelSerializer):
    is_present = serializers.BooleanField()
    is_late = serializers.BooleanField()
    grade_on_lesson = serializers.IntegerField()
    
    class Meta:
        model = Attendance
        fields = ['is_present', 'is_late', 'grade_on_lesson']

class StudentProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    avatar = serializers.ImageField(source='user.avatar')
    attendance = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = ['first_name', 'last_name', 'avatar', 'attendance']
    
    def get_attendance(self, obj):
        lesson = self.context.get('lesson')
        if lesson:
            attendance = Attendance.objects.filter(lesson=lesson, student=obj).first()
            if attendance:
                return AttendanceSerializer(attendance).data
        return None

class LessonTodaySerializer(serializers.ModelSerializer):
    teacher = TeacherProfileSerializer()
    students = serializers.SerializerMethodField()
    today_lessons = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'today_lessons', 'title', 'description', 'teacher', 'students']

    def get_students(self, obj):
        group = obj.group
        students = group.students.all()
        return StudentProfileSerializer(students, many=True, context={'lesson': obj}).data
    
    def get_today_lessons(self, obj):
        today_lessons = self.context.get('today_lessons', [])
        return LessonScheduleSerializer(today_lessons, many=True).data