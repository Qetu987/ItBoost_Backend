from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from course.models import Course, CourseMatherial
from course.serrializers import CourseSerializer, CourseMaterialSerializer
from user.permissions import IsTeacher, IsStudent

class CourseMaterialView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        course_id = request.query_params.get('course_id')

        courses = Course.objects.all()
        courses_serializer = CourseSerializer(courses, many=True)

        current_course = None
        current_course_data = None
        if course_id:
            current_course = Course.objects.filter(id=course_id).first()
        else:
            current_course = courses.first()

        if current_course:
            current_course_data = CourseSerializer(current_course).data
            materials = CourseMatherial.objects.filter(course=current_course)
            materials_serializer = CourseMaterialSerializer(materials, many=True)
            current_course_data['materials'] = materials_serializer.data

        response_data = {
            'courses': courses_serializer.data,
            'current_course': current_course_data
        }

        return Response(response_data)