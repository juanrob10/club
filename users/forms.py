from django import forms
from .models import Student,Teacher,CustomUser
from django.core.exceptions import ValidationError
from .USER_TYPES import STUDENT,TEACHER
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class CustomUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """
    class Meta:
        model = CustomUser
        fields = "__all__"
    """
    def save(self,commit=True):
        instance = super().save()        

        if instance.user_type == STUDENT:
           student = Student.objects.create(user=instance)
                           
        elif instance.user_type == TEACHER:
            teacher = Teacher.objects.create(user=instance)
        
        return  instance       
    """
class CustomUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    class Meta:
        model = CustomUser
        fields = "__all__"
    """
    def save(self,commit=True):
        instance = super().save(commit=False)
        # Realiza tus acciones personalizadas aquí antes de guardar los datos
        if instance.user_type == STUDENT:
            if hasattr(instance, 'teacher'):
                instance.teacher.delete()
           
            if not hasattr(instance, 'student'):
                instance.save()
                commit=False
                student = Student.objects.create(user=instance)
                    
        elif instance.user_type == TEACHER:
            if hasattr(instance, 'student'):
                instance.student.delete()
           
            if not hasattr(instance, 'teacher'):
                instance.save()
                commit=False
                teacher = Teacher.objects.create(user=instance)
        if commit:
            instance.save()
        return  instance        
    """


class StudentForm(forms.ModelForm):
    class Meta:
        model=Student
        fields = "__all__"


    def clean(self):
       
        cleaned_data = super().clean()
        user = cleaned_data.get('user')  # Obtener el valor del campo "user" del formulario
       
        # Obtener el valor anterior del campo "user" desde la instancia del modelo
        previous_user = None
        if self.instance and instance.pk:
            previous_user = instance.user
      
        if previous_user:
            #edit mode
            if user != previous_user:
                 raise ValidationError("Este usuario ya tiene otra relacion de estudiante o profesor")
        
        else :
            #creation mode
            raise ValidationError("No se permite crear una instacia Student")
        
        return cleaned_data  
    
class TeacherForm(forms.ModelForm):
    class Meta:
        model=Teacher
        fields = "__all__"


    def clean(self):
        #validaciones ya implementadas
        cleaned_data = super().clean()
        user = cleaned_data.get('user')  # Obtener el valor del campo "user" del formulario

        # Obtener el valor anterior del campo "user" desde la instancia del modelo
        instance = self.instance
        previous_user = None
    
        if instance and instance.pk:
            previous_user = instance.user
    
        if previous_user:
            #edit mode
            if user != previous_user:
                 self.cleaned_data['user'] = previous_user
                 raise ValidationError("Este usuario ya tiene otra relacion de estudiante o profesor")
        else:
            #creation mode
            raise ValidationError("No se permite crear una instacia Teacher")

        return cleaned_data    





