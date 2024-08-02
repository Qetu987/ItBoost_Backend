from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from education.serializers import CustomDataSerializer
from education.models import Homework, Submission, Attendance, Lesson
from user.models import CustomUser
from datetime import datetime



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