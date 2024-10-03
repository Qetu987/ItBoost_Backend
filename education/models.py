from django.db import models
from user.models import ModeratorProfile, StudentProfile, TeacherProfile
from course.models import Course, CourseMatherial

class Group(models.Model):
    title = models.CharField('Name of group', max_length=300, unique=True, blank=False, null=False)
    desc = models.TextField('Group description', blank=True, null=True)
    poster = models.ImageField("Group image", upload_to="Group/", blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add=True, verbose_name="date of create", blank=True)
    owner = models.ForeignKey(ModeratorProfile, verbose_name="Creator", related_name='groups', on_delete=models.CASCADE)
    students = models.ManyToManyField(StudentProfile, verbose_name="Students", related_name='group', blank=True)

    def __str__(self):
        return f'{self.id}_{self.title}'
    

class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name="Course", related_name='lessons', on_delete=models.CASCADE)
    course_material = models.ForeignKey(CourseMatherial, verbose_name="Material of lesson", related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField('Lesson title', max_length=300, blank=True, null=True)
    description = models.TextField('Lesson description', blank=True, null=True)
    pdf_material = models.FileField('Lesson PDF Material', upload_to='lessons/pdfs/', blank=True, null=True)
    lesson_url = models.URLField('Lesson meet URL', blank=True, null=True)
    video_url = models.URLField('Lesson Video URL', blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add=True, verbose_name="Date of create")
    lesson_date = models.DateTimeField('Lesson Date and Time', blank=True, null=True)
    teacher = models.ForeignKey(TeacherProfile, verbose_name="Teacher", related_name='lessons', on_delete=models.CASCADE)
    duration = models.IntegerField('Duration', blank=True, null=True, default=90)
    group = models.ForeignKey(Group, verbose_name="Group", related_name='lessons', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id}_{self.title}'


class Homework(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name="Lesson", related_name='homeworks', on_delete=models.CASCADE)
    title = models.CharField('Homework title', max_length=300, blank=False, null=False)
    description = models.TextField('Homework description', blank=True, null=True)
    homework_file = models.FileField('Lesson PDF Homework', upload_to='homeworks/files/', blank=True, null=True)
    due_date = models.DateTimeField('Due date')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name="Date of create")

    def __str__(self):
        return f'{self.id}_{self.title}'


class Submission(models.Model):
    homework = models.ForeignKey(Homework, verbose_name="Homework", related_name='submissions', on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, verbose_name="Student", related_name='submissions', on_delete=models.CASCADE)
    file = models.FileField('Submission file', upload_to='submissions/', blank=True, null=True)
    date_submitted = models.DateTimeField(auto_now_add=True, verbose_name="Date submitted")
    grade = models.IntegerField('Grade', blank=True, null=True)
    comment = models.TextField('Comment', blank=True, null=True)
    comment_from_teacher = models.TextField('Comment from teacher', blank=True, null=True)

    def __str__(self):
        return f'{self.id}_{self.student.user.username}_{self.homework.title}'
    

class Attendance(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name="Lesson", related_name='attendances', on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, verbose_name="Student", related_name='attendances', on_delete=models.CASCADE)
    grade_on_lesson = models.IntegerField("lesson grade", blank=True, null=True)
    grade_on_test = models.IntegerField("lesson grade", blank=True, null=True)
    is_present = models.BooleanField("Is present", default=False)
    is_late = models.BooleanField("Is late", default=False)
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date")

    class Meta:
        unique_together = ('lesson', 'student')

    def __str__(self):
        return f'{self.id}_{self.student.user.username}_{self.lesson.title}'
    

class LessonGrade(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name="Lesson", related_name='grades', on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, verbose_name="Student", related_name='lesson_grades', on_delete=models.CASCADE)
    grade = models.IntegerField("Grade")
    comment = models.TextField("Comment", blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, verbose_name="Date")

    def __str__(self):
        return f'{self.id}_{self.student.user.username}_{self.lesson.title}'