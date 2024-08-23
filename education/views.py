from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from education.serializers import (
    StudentDushboardSerializer, 
    TeacherDushboardSerializer, 
    ScheduleSerializer, 
    LessonTodaySerializer,
    LessonThemeUpdateSerializer
    )
from education.models import Homework, Submission, Attendance, Lesson
from datetime import datetime, timedelta
from django.utils import timezone
from user.permissions import IsTeacher



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

    def get(self, request):
        data = self.prepare_schedule_data(request)
        if isinstance(data, Response):
            return data

        serializer = ScheduleSerializer(data)
        return Response(serializer.data)
    

class TodayLessonScheduleView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request, lesson_id=None):
        today = timezone.now().date()
        teacher = request.user.teacherprofile

        lessons = Lesson.objects.filter(teacher=teacher, lesson_date__date=today)
        today_lessons = Lesson.objects.filter(teacher=teacher, lesson_date__date=today)
        if lesson_id:
            lessons = lessons.filter(id=lesson_id)

        if not lessons.exists():
            if not lesson_id:
                lessons = Lesson.objects.filter(teacher=teacher, lesson_date__date=today).order_by('lesson_date')
            if not lessons.exists():
                return Response({"detail": "No lessons found for today."}, status=404)
            
        lesson = lessons.first()

        serializer = LessonTodaySerializer(lesson, context={'today_lessons': today_lessons})
        return Response(serializer.data)

class LessonThemeView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

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