import json
from django.core.management.base import BaseCommand
from course.models import Course, CourseMatherial
from django.contrib.auth.hashers import make_password
from education.models import Group, Lesson, LessonGrade, Homework, Submission, Attendance
from user.models import CustomUser, ModeratorProfile, StudentProfile, TeacherProfile

class Command(BaseCommand):
    help = 'Import data from JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file')

    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']
        try:
            with open(json_file, 'r') as file:
                data = json.load(file)
            self.import_data(data)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to read file: {e}"))
    
    def import_data(self, data):
        for table_name, table_data in data.items():
            import_function = getattr(self, f"import_{table_name.lower()}", None)
            if import_function:
                try:
                    import_function(table_data)
                    self.stdout.write(self.style.SUCCESS(f"OK - {table_name} imported"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"ERROR - {table_name} not imported: {e}"))
            else:
                self.stdout.write(self.style.WARNING(f"WARNING - No import function for {table_name}"))
        else:
            self.stdout.write(self.style.SUCCESS('Data imported successfully'))

    def import_user(self, table_data):
        for row in table_data:
            CustomUser.objects.create_user(**row)

    def import_course(self, table_data):
        for row in table_data:
            owner = ModeratorProfile.objects.get(user_id=row.pop('owner_id'))
            Course.objects.create(owner=owner, **row)

    def import_coursematerial(self, table_data):
        for row in table_data:
            course = Course.objects.get(title=row.pop('course_title'))
            materials = row.pop('materials')
            for material in materials:
                owner = ModeratorProfile.objects.get(user_id=material.pop('owner_id'))
                CourseMatherial.objects.create(owner=owner, course=course, **material)

    def import_group(self, table_data):
        for row in table_data:
            owner = ModeratorProfile.objects.get(user_id=row.pop('owner_id'))
            students_ids = row.pop('students')
            group = Group.objects.create(owner=owner, **row)
            for id in students_ids:
                group.students.add(StudentProfile.objects.get(user_id=id))
    
    def import_lesson(self, table_data):
        for row in table_data:
            teacher = TeacherProfile.objects.get(user_id=row.pop('teacher'))
            group = Group.objects.get(title=row.pop('group_title'))
            course = Course.objects.get(title=row.pop('course'))
            course_material = CourseMatherial.objects.get(title = row.pop('matherial_title'), course=course)
            Lesson.objects.create(teacher=teacher, group=group, course=course, course_material=course_material, **row)

    def import_homework(self, table_data):
        for row in table_data:
            lesson = Lesson.objects.get(id=row.pop('lesson'))
            Homework.objects.create(lesson=lesson, **row)

    def import_submission(self, table_data):
        for row in table_data:
            homework = Homework.objects.get(id=row.pop('homework'))
            student = StudentProfile.objects.get(user_id=row.pop('student'))
            Submission.objects.create(homework=homework, student=student, **row)

    def import_attendance(self, table_data):
        for row in table_data:
            lesson = Lesson.objects.get(id=row.pop('lesson'))
            student = StudentProfile.objects.get(user_id=row.pop('student'))
            Attendance.objects.create(lesson=lesson, student=student, **row)