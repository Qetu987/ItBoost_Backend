# Generated by Django 5.0.6 on 2024-07-11 23:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('education', '0004_alter_lesson_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homework',
            name='title',
            field=models.CharField(max_length=300, verbose_name='Homework title'),
        ),
    ]
