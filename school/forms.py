from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from users.models import Student,Teacher
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.utils.translation import gettext_lazy as _

from .models import Message


from django.contrib.auth.forms import PasswordChangeForm


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

    def clean_username(self):
        username = self.cleaned_data['username']
        # Realiza validaciones personalizadas para el campo 'username'
        # Puedes agregar lógica adicional aquí y lanzar ValidationError si es necesario
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        # Realiza validaciones personalizadas para el campo 'password'
        # Puedes agregar lógica adicional aquí y lanzar ValidationError si es necesario
        return password
  