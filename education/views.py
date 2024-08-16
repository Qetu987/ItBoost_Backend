from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from education.serializers import CustomDataSerializer, ScheduleSerializer, LessonTodaySerializer
from education.models import Homework, Submission, Attendance, Lesson
from datetime import datetime, timedelta
from django.utils.timezone import now
from user.permissions import IsTeacher



class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def prepear_data(seld, request):
        user = request.user

        # Подсчитываем количество домашних заданий
        homeworks_count = Homework.objects.filter(lesson__group__students__user=user).count()

        # Считаем среднюю оценку
        submissions = Submission.objects.filter(student__user=user)
        total_grades = sum([submission.grade for submission in submissions if submission.grade is not None])
        average_mark = total_grades / submissions.count() if submissions.count() > 0 else 0

        # Посещенные уроки
        attendances = Attendance.objects.filter(student__user=user)
        lesson_visited = {
            'all': attendances.count(),
            'visited': attendances.filter(is_present=True).count()
        }

        # Будущие уроки (например, уроки после сегодняшней даты)
        future_lessons = Lesson.objects.filter(group__students__user=user, date_create__gt=datetime.now())

        return {
            'user': user,
            'homeworks': homeworks_count,
            'average_mark': average_mark,
            'lesson_visited': lesson_visited,
            'future_lessons': future_lessons
        }


    def get(self, request):
        data = self.prepear_data(request)

        serializer = CustomDataSerializer(data)
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
            week_lessons = Lesson.objects.filter(
                group__students__user=user,
                lesson_date__range=self.search_week_days(search_date)
            )

            month_lessons = Lesson.objects.filter(
                group__students__user=user,
                lesson_date__range=self.search_month_days(search_date)
            )
        else:
            week_lessons = Lesson.objects.filter(
                teacher__user=user,
                lesson_date__range=self.search_week_days(search_date)
            )

            month_lessons = Lesson.objects.filter(
                teacher__user=user,
                lesson_date__range=self.search_month_days(search_date)
            )

        return {
            'week': week_lessons,
            'month': month_lessons
        }
    
    def search_month_days(self, search_date):
        first_day_of_month = search_date.replace(day=1)
        last_day_of_month = (search_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return [first_day_of_month, last_day_of_month]
    
    def search_week_days(self, search_date):
        start_of_week = search_date - timedelta(days=search_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return [start_of_week, end_of_week]

    def get(self, request):
        data = self.prepare_schedule_data(request)
        if isinstance(data, Response):
            return data

        serializer = ScheduleSerializer(data)
        return Response(serializer.data)
    

class TodayLessonScheduleView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request, lesson_id=None):
        today = now().date()
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
