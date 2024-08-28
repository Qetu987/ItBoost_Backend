from rest_framework import serializers
from education.models import Lesson, Attendance, Group, Homework, Submission
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
    id = serializers.IntegerField(source='user_id', read_only=True)

    class Meta:
        model = StudentProfile
        fields = ['id', 'first_name', 'last_name', 'avatar', 'attendance']
    
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
    course = CourseSerializer(read_only=True)
    group = GroupSerializer(read_only=True)


    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'course', 'group', 'teacher', 'students', 'duration', 'lesson_date', 'date_create']

    def get_students(self, obj):
        group = obj.group
        students = group.students.all()
        return StudentProfileSerializer(students, many=True, context={'lesson': obj}).data


class LessonThemeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['title', 'description']


class AttendanceUserCheckUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['is_present', 'is_late']


class AttendanceMarkUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['grade_on_lesson']

class HomeworkSetSerializer(serializers.ModelSerializer):
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all())
    homework_file = serializers.FileField(max_length=None, allow_empty_file=False, use_url=True, required=False)

    class Meta:
        model = Homework
        fields = ['id', 'lesson', 'title', 'description', 'homework_file', 'due_date']

    def create(self, validated_data):
        homework = Homework.objects.create(**validated_data)
        return homework



class LessonHomeworkSerializer(serializers.ModelSerializer):
    teacher = TeacherProfileSerializer()
    course = CourseSerializer(read_only=True)
    group = GroupSerializer(read_only=True)


    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'course', 'group', 'teacher', 'duration', 'lesson_date', 'date_create']

class HomeworkWievSerializer(serializers.ModelSerializer):
    lesson = LessonHomeworkSerializer()

    class Meta:
        model = Homework
        fields = ['id', 'lesson', 'title', 'description', 'homework_file', 'due_date', 'date_create']


class SubmissionWievSerializer(serializers.ModelSerializer):
    homework = HomeworkWievSerializer()

    class Meta:
        model = Submission
        fields = ['id', 'homework', 'student', 'file', 'date_submitted', 'grade', 'comment']


class SubmissionCreateSerializer(serializers.ModelSerializer):
    homework = serializers.PrimaryKeyRelatedField(queryset=Homework.objects.all())
    file = serializers.FileField(max_length=None, allow_empty_file=False, use_url=True, required=False)

    class Meta:
        model = Submission
        fields = ['id', 'homework', 'student', 'file', 'date_submitted', 'comment']

    def create(self, validated_data):
        submission = Submission.objects.create(**validated_data)
        return submission
    

class SubmissionSetMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['grade', 'comment_from_teacher']


class SubmissionListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'file', 'date_submitted', 'comment', 'grade']

class HomeworkListSerializer(serializers.ModelSerializer):
    submission = serializers.SerializerMethodField()
    lesson = LessonHomeworkSerializer()

    class Meta:
        model = Homework
        fields = ['id', 'lesson', 'title', 'description', 'homework_file', 'due_date', 'date_create', 'submission']

    def get_submission(self, obj):
        student = self.context['request'].user.studentprofile  # Получаем студента из контекста запроса
        submission = Submission.objects.filter(homework=obj, student=student).first()
        if submission:
            return SubmissionListViewSerializer(submission).data
        return None