from rest_framework import serializers
from education.models import Lesson, Attendance, Group
from user.models import StudentProfile
from user.serializers import TeacherProfileSerializer
from course.serrializers import CourseSerializer


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'title', 'desc', 'poster', 'owner']

class LessonScheduleSerializer(serializers.ModelSerializer):
    teacher = TeacherProfileSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    group = GroupSerializer(read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'date_create', 'lesson_date', 'duration', 'teacher', 'group']

class DushboardBaseSerializer(serializers.Serializer):
    future_lessons = LessonScheduleSerializer(many=True)

class StudentDushboardSerializer(DushboardBaseSerializer):
    homeworks = serializers.IntegerField()
    average_mark = serializers.FloatField()
    lesson_in_month = serializers.IntegerField()
    lesson_visited = serializers.DictField()

class TeacherDushboardSerializer(DushboardBaseSerializer):
    homeworks_count = serializers.IntegerField()

class ScheduleSerializer(serializers.Serializer):
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
        fields = ['id', 'today_lessons', 'title', 'description', 'teacher', 'students', 'duration', 'lesson_date']

    def get_students(self, obj):
        group = obj.group
        students = group.students.all()
        return StudentProfileSerializer(students, many=True, context={'lesson': obj}).data
    
    def get_today_lessons(self, obj):
        today_lessons = self.context.get('today_lessons', [])
        return LessonScheduleSerializer(today_lessons, many=True).data