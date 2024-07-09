from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import CustomUser, StudentProfile, TeacherProfile, ModeratorProfile

@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'student':
            StudentProfile.objects.create(user=instance)
        elif instance.role == 'teacher':
            TeacherProfile.objects.create(user=instance)
        elif instance.role == 'moderator':
            ModeratorProfile.objects.create(user=instance)
    else:
        # Обновление существующего пользователя
        if instance.role == 'student' and not hasattr(instance, 'studentprofile'):
            StudentProfile.objects.create(user=instance)
        elif instance.role == 'teacher' and not hasattr(instance, 'teacherprofile'):
            TeacherProfile.objects.create(user=instance)
        elif instance.role == 'moderator' and not hasattr(instance, 'moderatorprofile'):
            ModeratorProfile.objects.create(user=instance)
        # Убедитесь, что старые профили удалены
        if instance.role != 'student' and hasattr(instance, 'studentprofile'):
            instance.studentprofile.delete()
        if instance.role != 'teacher' and hasattr(instance, 'teacherprofile'):
            instance.teacherprofile.delete()
        if instance.role != 'moderator' and hasattr(instance, 'moderatorprofile'):
            instance.moderatorprofile.delete()

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'student' and hasattr(instance, 'studentprofile'):
        instance.studentprofile.save()
    elif instance.role == 'teacher' and hasattr(instance, 'teacherprofile'):
        instance.teacherprofile.save()
    elif instance.role == 'moderator' and hasattr(instance, 'moderatorprofile'):
        instance.moderatorprofile.save()