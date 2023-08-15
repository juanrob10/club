from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from users.models import Student,Teacher
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.utils.translation import gettext_lazy as _
from .models import Session

from .models import Message
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from datetime import timedelta


class SessionForm(forms.ModelForm):

    class Meta:
        model= Session
        fields = "__all__"
    
    def clean_enrolled_package(self):
        enrolled_package  = self.cleaned_data.get('enrolled_package')

        if not enrolled_package.status:
            raise ValidationError("No puedes crear una sesion por que el paquete  al que pertenece esta incativo")
        return enrolled_package 
    
    def clean(self):
        cleaned_data = super().clean()
        
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        session_duration = end_time - start_time
        time_0 = timedelta(days=0, hours=0, minutes=0, seconds=0)
        
        if session_duration <= time_0 :
            raise ValidationError("El tiempo de sesion no puede ser  cero o negativo")
        
        return  cleaned_data 


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Establecer placeholders para los campos del formulario
        self.fields['old_password'].widget.attrs['placeholder'] = 'Contraseña actual'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Nueva contraseña'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Repetir nueva contraseña'


class MessageCreationForm(forms.ModelForm):
    phone = PhoneNumberField(widget=PhoneNumberPrefixWidget(),required=False,label='Teléfono')
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Mensaje'}),
        label='Mensaje'  # Etiqueta del campo
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer el atributo placeholder para el campo de teléfono
        self.fields['phone'].widget.attrs['placeholder'] = 'Teléfono'

    class Meta:
        model = Message
        fields = ['name', 'email', 'concern', 'message', 'phone']
    
        widgets = {
                'name': forms.TextInput(attrs={'placeholder': 'Nombre'}),
                'email': forms.EmailInput(attrs={'placeholder': 'Correo Electrónico'}),
                'concern': forms.TextInput(attrs={'placeholder': 'Asunto'})
            }


class CustomerUserForm(forms.ModelForm):

 
    class Meta:
        model = get_user_model()
        fields = ("username","email","first_name","last_name","date_joined")
        widgets = {
            'date_joined': forms.DateInput(attrs={'type': 'date', 'format': '%Y-%m-%d','readonly': 'readonly'}),
        }
     
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        instance = kwargs.get('instance')
    
        if instance:
    
            if hasattr(instance, 'student'):
                self.fields['picture'] = forms.ImageField(required=True,label="Imagen")
                self.fields['date_birth'] = forms.DateField(required=False,widget=forms.DateInput(attrs={'type': 'date', 'format': '%Y-%m-%d'}),label="Fecha de nacimiento")
                self.fields['tutor_name'] = forms.CharField(max_length=100, required=False,label="Nombre del Tutor")
                self.fields['tutor_number'] = PhoneNumberField(widget=PhoneNumberPrefixWidget(),required=False,label="Número del Tutor")
            elif hasattr(instance, 'teacher'):
                self.fields['contact_number'] = PhoneNumberField(widget=PhoneNumberPrefixWidget(),required=False,label="Número de Contacto")

    def save(self, commit=True):
        instance = super().save(commit=False)
       
        if hasattr(instance, 'student'):
            student = instance.student    

            if self.cleaned_data['picture']:
                student.picture = self.cleaned_data['picture']
            else :
                 student.picture = None      
            student.date_birth = self.cleaned_data['date_birth']
            student.tutor_name = self.cleaned_data['tutor_name']
            student.tutor_number = self.cleaned_data['tutor_number']
            if commit:
                student.save()

        elif hasattr(instance, 'teacher'):
            teacher = instance.teacher
            teacher.contact_number = self.cleaned_data['contact_number']
            if commit:
                teacher.save()
       
        instance.save()

        return instance

class LoginForm(AuthenticationForm):
   
    username = forms.CharField(label='Usuario', max_length=100, widget=forms.TextInput(attrs={'class': '', 'placeholder': 'Ingrese su nombre de usuario'}))
    password = forms.CharField(label='Contraseña', max_length=100, widget=forms.PasswordInput(attrs={'class': '', 'placeholder': 'Ingrese su contraseña'}))


  