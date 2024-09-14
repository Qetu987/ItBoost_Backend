from rest_framework import serializers
from education.models import Lesson, Attendance, Group, Homework, Submission
from user.models import StudentProfile
from user.serializers import TeacherProfileSerializer, ProfileSerializer
from course.serrializers import CourseSerializer
from course.models import Course


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
        fields = ['id', 'first_name', 'last_name', 'age', 'avatar', 'attendance']
    
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


class StudentProfileForSubmissionSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    avatar = serializers.ImageField(source='user.avatar')
    id = serializers.IntegerField(source='user_id', read_only=True)
    group = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = StudentProfile
        fields = ['id', 'first_name', 'last_name', 'avatar', 'group']

class SubmissionWievSerializer(serializers.ModelSerializer):
    homework = HomeworkWievSerializer()
    student = StudentProfileForSubmissionSerializer()

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
    homework_file = serializers.SerializerMethodField()

    class Meta:
        model = Homework
        fields = ['id', 'lesson', 'title', 'description', 'homework_file', 'due_date', 'date_create', 'submission']

    def get_submission(self, obj):
        student = self.context['request'].user.studentprofile  # Получаем студента из контекста запроса
        submission = Submission.objects.filter(homework=obj, student=student).first()
        if submission:
            return SubmissionListViewSerializer(submission).data
        return None
    
    def get_homework_file(self, obj):
        if obj.homework_file:
            return obj.homework_file.url  # Это вернет относительный путь
        return None

class GroupDetailSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'title', 'desc', 'poster', 'students']

    def get_students(self, obj):
        students = obj.students.all()
        return ProfileSerializer(students, many=True, context={'group': obj}).data
    

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'desc', 'poster', 'date_create', 'Lesson_count']


class LessonStudentActivitySerializer(serializers.ModelSerializer):
    is_present = serializers.SerializerMethodField()
    is_late = serializers.SerializerMethodField()
    grade_on_lesson = serializers.SerializerMethodField()
    homework_grade = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'lesson_date', 'is_present', 'is_late', 'grade_on_lesson', 'homework_grade']

    def get_is_present(self, lesson):
        student = self.context['student']
        attendance = Attendance.objects.filter(lesson=lesson, student=student).first()
        return attendance.is_present if attendance else None

    def get_is_late(self, lesson):
        student = self.context['student']
        attendance = Attendance.objects.filter(lesson=lesson, student=student).first()
        return attendance.is_late if attendance else None

    def get_grade_on_lesson(self, lesson):
        student = self.context['student']
        grade = Attendance.objects.filter(lesson=lesson, student=student).first()
        return grade.grade_on_lesson if grade else None

    def get_homework_grade(self, lesson):
        student = self.context['student']
        homework = Homework.objects.filter(lesson=lesson).first()
        if homework:
            submission = Submission.objects.filter(homework=homework, student=student).first()
            return submission.grade if submission else None
        return None

class CourseDetailWithStudentLessonsSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'desc', 'poster', 'date_create', 'Lesson_count', 'lessons']

    def get_lessons(self, course):
        student = self.context['student']
        lessons = Lesson.objects.filter(course=course, group__students=student)
        return LessonStudentActivitySerializer(lessons, many=True, context={'student': student}).data