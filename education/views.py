from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from education.serializers import (
    StudentDushboardSerializer, 
    TeacherDushboardSerializer, 
    ScheduleSerializer, 
    LessonTodaySerializer,
    LessonThemeUpdateSerializer,
    AttendanceUserCheckUpdateSerializer,
    AttendanceMarkUpdateSerializer,
    HomeworkSetSerializer,
    )
from education.models import Homework, Submission, Attendance, Lesson
from datetime import datetime, timedelta
from django.utils import timezone
from user.permissions import IsTeacher
from user.models import StudentProfile



class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def unsubmitted_homework_count(self, user):
        submitted_homework_ids = Submission.objects.filter(student__user=user).values_list('homework_id', flat=True)

        return Homework.objects.filter(
            lesson__group__students__user=user
        ).exclude(
            id__in=submitted_homework_ids
        ).count()

    def average_mark(self, user):
        submissions = Submission.objects.filter(student__user=user)
        attendances = Attendance.objects.filter(student__user=user)
        submissions_total_grades = [submission.grade for submission in submissions if submission.grade is not None]
        attendances_lessons_total_grades = [attendance.grade_on_lesson for attendance in attendances if attendance.grade_on_lesson is not None]
        attendances_test_total_grades = [attendance.grade_on_test for attendance in attendances if attendance.grade_on_test is not None]
        total_grades = list()
        total_grades.extend(submissions_total_grades)
        total_grades.extend(attendances_lessons_total_grades)
        total_grades.extend(attendances_test_total_grades)

        return sum(total_grades) / len(total_grades) if len(total_grades) > 0 else 0

    def lesson_in_month(self, user):
        date = timezone.localtime()
        first_day_of_month = date.replace(day=1)
        last_day_of_month = (date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        monthly_lessons = Lesson.objects.filter(
            group__students__user=user,
            lesson_date__range=[first_day_of_month, last_day_of_month]
        )
        return monthly_lessons.count()

    def lesson_visited(self, user): 
        attendances = Attendance.objects.filter(student__user=user)
        return {
            'all': attendances.count(),
            'visited': attendances.filter(is_present=True).count()
        }
    
    def student_lessons_list(self, user):
        current_time = timezone.localtime()
        two_weeks_later = current_time + timedelta(weeks=2)
        return Lesson.objects.filter(
            group__students__user=user, 
            lesson_date__range=[current_time, two_weeks_later]
        )
    
    def teacher_lessons_list(self, user):
        current_time = timezone.localtime()
        two_weeks_later = current_time + timedelta(weeks=2)
        return Lesson.objects.filter(
            teacher__user=user, 
            lesson_date__range=[current_time, two_weeks_later]
        )

    def teacher_homeworks_count(self, user):
        lessons_by_teacher = Lesson.objects.filter(teacher__user=user)
        homeworks_by_teacher = Homework.objects.filter(lesson__in=lessons_by_teacher)
        ungraded_homeworks = Submission.objects.filter(
            homework__in=homeworks_by_teacher, 
            grade__isnull=True
            )
        return ungraded_homeworks.count()

    def prepear_data(self, request):
        user = request.user

        if user.role == 'student':
            return {
                'homeworks': self.unsubmitted_homework_count(user),
                'average_mark': self.average_mark(user),
                'lesson_in_month': self.lesson_in_month(user),
                'lesson_visited': self.lesson_visited(user),
                'future_lessons': self.student_lessons_list(user)
            }
        else:
            return {
                'homeworks_count': self.teacher_homeworks_count(user),
                'future_lessons': self.teacher_lessons_list(user)
            }

    @swagger_auto_schema(
        operation_summary="Get User Dashboard",
        operation_description="Provides detailed dashboard data for students or teachers based on their roles.",
        responses={
            200: 'Dynamic dashboard data returned based on user role',
            400: 'Bad request if the user role is not handled'
        },
        tags=['Dashboard']
    )
    def get(self, request):
        data = self.prepear_data(request)

        if request.user.role == 'student':
            serializer = StudentDushboardSerializer(data)
        elif request.user.role == 'teacher':
            serializer = TeacherDushboardSerializer(data)
        else:
            return Response({"detail": "User has not data to dashboard."}, status=400)
        return Response(serializer.data)

class ScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def prepare_schedule_data(self, request):
        user = request.user
        search_date = request.query_params.get('start_date')

        if not search_date:
            return Response({"detail": "Start date is required."}, status=400)
        try:
            search_date = datetime.fromisoformat(search_date)
        except ValueError:
            return Response({"detail": "Invalid date format. Use ISO format."}, status=400)

        if user.role == 'student':
            month_lessons = Lesson.objects.filter(
                group__students__user=user,
                lesson_date__range=self.search_month_days(search_date)
            )
        else:
            month_lessons = Lesson.objects.filter(
                teacher__user=user,
                lesson_date__range=self.search_month_days(search_date)
            )

        return {
            'month': month_lessons
        }
    
    def search_month_days(self, search_date):
        first_day_of_month = search_date.replace(day=1)
        last_day_of_month = (search_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return [first_day_of_month, last_day_of_month]

    @swagger_auto_schema(
        operation_summary="Retrieve Schedule",
        operation_description="Retrieves the schedule for a month based on the given start date.",
        manual_parameters=[
            openapi.Parameter(
                name='start_date',
                in_=openapi.IN_QUERY,
                description='Start date of the month to retrieve schedule for (in ISO format).',
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: ScheduleSerializer(),
            400: "Start date is required or Invalid date format. Use ISO format."
        }
    )
    def get(self, request):
        data = self.prepare_schedule_data(request)
        if isinstance(data, Response):
            return data

        serializer = ScheduleSerializer(data)
        return Response(serializer.data)
    

class TodayLessonScheduleView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    @swagger_auto_schema(
        operation_summary="Get today's lessons",
        operation_description="Retrieves a list of today's lessons for the current teacher.",
        responses={
            200: LessonTodaySerializer(many=True),
            404: 'No lessons found for today.'
        },
        tags=['Lessons']
    )
    def get(self, request):
        today = timezone.now().date()
        teacher = request.user.teacherprofile

        lessons = Lesson.objects.filter(teacher=teacher, lesson_date__date=today).order_by('lesson_date')

        if not lessons.exists():
            if not lessons.exists():
                return Response({"detail": "No lessons found for today."}, status=404)

        serializer = LessonTodaySerializer(lessons, many=True, context={'request': request})
        return Response(serializer.data)

class LessonThemeView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    @swagger_auto_schema(
        operation_summary="Update Lesson Theme",
        operation_description="Updates the theme of a lesson and marks attendance for all students as not present and not late.",
        request_body=LessonThemeUpdateSerializer,
        responses={
            200: openapi.Response('Success', examples={"application/json": {"message": "Success"}}),
            400: openapi.Response('Bad Request', examples={"application/json": {"detail": "Error message"}}),
            404: 'Lesson not found if the lesson_id does not exist'
        },
        tags=['Lessons']
    )
    def post(self, request, lesson_id):
        lesson = Lesson.objects.get(id=lesson_id)
        serializer = LessonThemeUpdateSerializer(lesson, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            group = lesson.group
            students = group.students.all()
            for student in students:
                attendance, created = Attendance.objects.get_or_create(
                    lesson=lesson,
                    student=student,
                    defaults={'is_present': False, 'is_late': False}
                )
                attendance.save()
            return Response({"message": "Success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AttendanceUserCheckView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    @swagger_auto_schema(
        operation_summary="Update Attendance Record",
        operation_description="Updates an attendance record for a specified student and lesson. Creates a new record if it does not exist.",
        request_body=AttendanceUserCheckUpdateSerializer,
        responses={
            200: openapi.Response('Success', examples={"application/json": {"message": "Success"}}),
            400: openapi.Response('Bad Request', examples={
                "application/json": {
                    "detail": "Invalid data. Attendance is not create.",
                    "detail": "Invalid user. Curent user is not a teacher in this lesson.",
                    "detail": "Invalid data. Properties 'is_present' or 'is_late' not in request body.",
                    }
                }),
            404: 'Lesson or student not found'
        },
        tags=['Attendance']
    )
    def post(self, request, lesson_id, student_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except:
            return Response({"detail": "Invalid lesson. Curent lesson does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        student = StudentProfile.objects.get(user_id=student_id)
        attendance = Attendance.objects.filter(lesson=lesson, student=student).first()
        
        if lesson.teacher.user != request.user:
            return Response({"detail": "Invalid user. Curent user is not a teacher in this lesson."}, status=status.HTTP_400_BAD_REQUEST)
        
        if attendance is None:
            return Response({"detail": "Invalid data. Attendance is not create."}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {
            'is_present': request.data.get('is_present'),
            'is_late': request.data.get('is_late'),
            }
        
        if data['is_present'] == None or data['is_late'] == None:
            return Response({"detail": "Invalid data. Properties 'is_present' or 'is_late' not in request body."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AttendanceUserCheckUpdateSerializer(attendance, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AttendanceMarkCheckView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    @swagger_auto_schema(
        operation_summary="Update Lesson Attendance Grade",
        operation_description="Updates the attendance grade for a specified student and lesson. Checks if the student is marked present before updating the grade.",
        request_body=AttendanceMarkUpdateSerializer,
        responses={
            200: openapi.Response('Success', examples={"application/json": {"message": "Success"}}),
            400: openapi.Response('Bad Request', examples={
                "application/json": {
                    "detail": "Invalid user. Current user is not a teacher in this lesson.",
                    "detail": "Invalid user checking. Current student is absent in this lesson.",
                    "detail": "Invalid data. Attendance record is not created.",
                    "detail": "Invalid data. Properties 'grade_on_lesson' not in request body."
                }
            }),
            404: 'Lesson or student not found'
        },
        tags=['Attendance']
    )
    def post(self, request, lesson_id, student_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except:
            return Response({"detail": "Invalid lesson. Curent lesson does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        
        student = StudentProfile.objects.get(user_id=student_id)
        attendance = Attendance.objects.filter(lesson=lesson, student=student).first()

        if lesson.teacher.user != request.user:
            return Response({"detail": "Invalid user. Curent user is not a teacher in this lesson."}, status=status.HTTP_400_BAD_REQUEST)
        
        if attendance.is_present != True:
            return Response({"detail": "Invalid user Checking. Curent student is absent in this lesson."}, status=status.HTTP_400_BAD_REQUEST)
        
        if attendance is None:
            return Response({"detail": "Invalid data. Attendance is not create."}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {'grade_on_lesson': request.data.get('grade_on_lesson')}
        
        if data['grade_on_lesson'] == None:
            return Response({"detail": "Invalid data. Properties 'grade_on_lesson' not in request body."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AttendanceMarkUpdateSerializer(attendance, data=data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class HomeworksSetView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    @swagger_auto_schema(
        operation_summary="Set homework",
        operation_description="Set homework for students in the lesson. Checks if lesson already exist and if user is owner of curent lesson.",
        request_body=HomeworkSetSerializer,
        responses={
            200: openapi.Response('Created', examples={"application/json": {"message": "Success"}}),
            400: openapi.Response('Bad Request', examples={
                "application/json": {
                    "detail": "Invalid data. Properties 'lesson' or 'title' or 'due_date' not in request body.",
                    "detail": "Invalid user. Curent user is not a teacher in this lesson.",
                    "detail": "Invalid user. Current user is not a teacher in this lesson.",
                    "detail": "Invalid pk \"50\" - object does not exist."
                }
            }),
            404: 'Lesson or student not found'
        },
        tags=['Attendance']
    )
    def post(self, request):
        
        data = {
            'lesson': request.data.get('lesson'),
            'title': request.data.get('title'),
            'due_date': request.data.get('due_date'),
            }

        if data['lesson'] == None or data['title'] == None or data['due_date'] == None:
            return Response({"detail": "Invalid data. Properties 'lesson' or 'title' or 'due_date' not in request body."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = HomeworkSetSerializer(data=data)

        if serializer.is_valid():
            lesson = serializer.validated_data['lesson']
            
            if lesson.teacher.user != request.user:
                return Response({"detail": "Invalid user. Curent user is not a teacher in this lesson."}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            return Response({"message": "Created"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)