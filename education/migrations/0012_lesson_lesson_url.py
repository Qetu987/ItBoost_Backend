# Generated by Django 5.0.6 on 2024-10-03 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0011_alter_lesson_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='lesson_url',
            field=models.URLField(blank=True, null=True, verbose_name='Lesson meet URL'),
        ),
    ]
