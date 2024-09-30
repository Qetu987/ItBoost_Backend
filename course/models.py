from django.db import models
from user.models import ModeratorProfile

class Course(models.Model):
    title = models.CharField('Name of course', max_length=300, unique=True, blank=False, null=False)
    desc = models.TextField('Course description', blank=True, null=True)
    poster = models.ImageField("Course image", upload_to="course/", blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add=True, verbose_name="date of create", blank=True)
    owner = models.ForeignKey(ModeratorProfile, verbose_name="Creator", related_name='courses', on_delete=models.CASCADE)
    is_active = models.BooleanField("Is active", default=True)
    Lesson_count = models.IntegerField("Count of lessons in course", default=12)

    def __str__(self):
        return f'{self.id}_{self.title}'

class CourseMatherial(models.Model):
    course = models.ForeignKey(Course, verbose_name="Course", related_name='materials', on_delete=models.CASCADE)
    title = models.CharField('Name of material', max_length=300, blank=False, null=False)
    order_number = models.IntegerField("Order number", blank=True, null=True)
    desc = models.TextField('Material description', blank=True, null=True)
    pdf_file = models.FileField('File', upload_to='course/pdfs/', blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add=True, verbose_name="date of create", blank=True)
    owner = models.ForeignKey(ModeratorProfile, verbose_name="Creator", related_name='course_materials', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id}_{self.title}'