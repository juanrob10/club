from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser,Student, Teacher
from .USER_TYPES import STUDENT,TEACHER
from django.contrib.auth.signals import user_logged_in

@receiver(post_save, sender=CustomUser)
def update_profile(sender, instance,created,**kwargs):
   
    # Verificar si la instancia es nueva (se está creando) o se está actualizando
    if created:

        # Funcionalidad para la creación de la instancia
        if instance.user_type == STUDENT:
            student = Student.objects.create(user=instance)
        elif instance.user_type == TEACHER:
            teacher = Teacher.objects.create(user=instance)
    else:
        # Funcionalidad para la actualización de la instancia
        if instance.user_type == STUDENT:
            if hasattr(instance, 'teacher'):
                instance.teacher.delete()
            if not hasattr(instance, 'student'):
                student = Student.objects.create(user=instance)
            
        elif instance.user_type == TEACHER:
            if hasattr(instance, 'student'):
                instance.student.delete()
            if not hasattr(instance, 'teacher'):
                teacher = Teacher.objects.create(user=instance)

@receiver(user_logged_in)
def create_profile_on_login(sender, request, user, **kwargs):
 
    # Verificar si el usuario es un estudiante o un profesor
    if user.user_type == STUDENT:
        if not hasattr(user, 'student'):
            student = Student.objects.create(user=user)
    elif user.user_type == TEACHER:
        if not hasattr(user, 'teacher'):
            teacher = Teacher.objects.create(user=user)                
