from django.db import models

class CallBackRequest(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('in_progress', 'In progress'),
        ('not_interesting', 'Not interesting'),
        ('success', 'Success'),
        ('call_back', 'Call back'),
    )

    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    name = models.CharField('Name parrents', max_length=300, blank=False, null=False)
    age = models.IntegerField('age of child', null=False, blank=False)
    email = models.EmailField("email address", blank=True)
    phone_num = models.CharField('Phone number', max_length=300, blank=False, null=False)
    note = models.TextField('note of request', blank=True, null=True)
    date_create = models.DateTimeField(auto_now_add=True, verbose_name="Date of create")

    def __str__(self):
        return f'{self.id}'