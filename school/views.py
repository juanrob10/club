from django.shortcuts import render
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from .forms import LoginForm,CustomerUserForm,MessageCreationForm,CustomPasswordChangeForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model
from django.views.generic import UpdateView
from users.USER_TYPES import STUDENT,TEACHER
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.views.generic.edit import FormView,CreateView
from django.contrib.auth import update_session_auth_hash
from django.views.generic import ListView
from users.models import Student

from .models import EnrolledPackage,Session,Message
from django.shortcuts import get_object_or_404
from django.utils.translation import activate


from django.views import View


class CustomerUserUpdateView(LoginRequiredMixin,UpdateView):
    model = get_user_model()
    form_class = CustomerUserForm
    template_name = 'school/user_app/update_user.html'
    context_object_name = 'customer_user'
    success_url = reverse_lazy('school:user_detail') 

    def get_object(self, queryset=None):
        # Obtén el objeto del usuario logado
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, "¡Tu perfil ha sido actualizado exitosamente!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, "¡Hubo un error al enviar el formulario! Por favor, verifica los datos e inténtalo nuevamente.")
        return super().form_invalid(form)    

    def get_initial(self):
        initial = super().get_initial()
        instance = self.get_object()
        if instance.date_joined:
            initial['date_joined'] = instance.date_joined.strftime('%Y-%m-%d')

        if hasattr(instance, 'student'):
            if instance.student.picture:
                initial['picture'] = instance.student.picture
            if instance.student.date_birth:
                initial['date_birth'] = instance.student.date_birth.strftime('%Y-%m-%d')
            initial['tutor_name'] = instance.student.tutor_name
            initial['tutor_number'] = instance.student.tutor_number

        elif hasattr(instance, 'teacher'):
            initial['contact_number'] = instance.teacher.contact_number

        return initial
        

class CustomerUserDetailView(LoginRequiredMixin,DetailView):
    model = get_user_model()
    template_name = 'school/user_app/user_detail.html'  # Reemplaza 'customer_user_detail.html' con el nombre de tu plantilla de detalle
    context_object_name = 'customer_user'

    def get_object(self, queryset=None):
        # Obtén el objeto del usuario logado
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_type = self.object.user_type

        if user_type == STUDENT:
            student = self.object.student
            
            context['teacher'] = None
            context['student'] = student
         
        elif user_type == TEACHER:
            teacher = self.object.teacher
            
            context['teacher'] = teacher
            context['student'] = None
  

        return context


class MyLoginView(LoginView):
    template_name = 'school/user_app/login.html'
    authentication_form = LoginForm
  
    
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('school:user_detail')
        return super().dispatch(request, *args, **kwargs)
    
    def enviar_mensaje_bienvenida(self, nombre_usuario):
        mensaje = f"Bienvenido, {nombre_usuario}!"
        messages.success(self.request, mensaje)
    
    def form_valid(self, form):
        self.enviar_mensaje_bienvenida(form.get_user().username)
        return super().form_valid(form) 
    

class Index(TemplateView):
	template_name = 'school/landing_page/index.html'
        

class Inicio(LoginRequiredMixin,TemplateView):
    template_name = 'school/user_app/inicio.html'



class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = 'school/user_app/change_password.html'
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('school:user_detail')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)  # Actualizar la clave de autenticación de la sesión
        messages.success(self.request, 'Tu contraseña ha sido cambiada.')
        return super().form_valid(form)

class EnrolledPackageListView(LoginRequiredMixin,ListView):
    model = EnrolledPackage
    template_name = 'school/user_app/enrolled_package_list.html'
    context_object_name = 'enrolled_packages'
    

    def get_queryset(self):
        queryset = super().get_queryset()
        student_pk = self.kwargs['student_pk']
        student =  get_object_or_404(Student,pk=student_pk)
        return queryset.filter(student=student)


class SessionListView(LoginRequiredMixin,ListView):
    model = Session
    template_name = 'school/user_app/session_list.html'
    context_object_name = 'sessions'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        enrolled_package =  self.kwargs['enrolled_package'] 
        context["enrolled_package"] =  enrolled_package
        return context
    

    def get_queryset(self):
        queryset = super().get_queryset()
        enrolled_package_id= self.kwargs['enrolled_package_id']
        enrolled_package = get_object_or_404(EnrolledPackage,id=enrolled_package_id)
        self.kwargs['enrolled_package'] = enrolled_package
        return queryset.filter(enrolled_package=enrolled_package)



class CreateMessageView(LoginRequiredMixin,CreateView):
    model = Message
    template_name = 'school/user_app/inicio.html'
    form_class =  MessageCreationForm
    success_url = reverse_lazy('school:user_detail')

    def form_valid(self, form):
        messages.success(self.request, "¡Tu mensaje se ha enviado exitosamente!")
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        user =  self.request.user

        if self.request.user.is_authenticated:
            initial['name'] = user.first_name+ " "+ user.last_name
            initial['email'] = user.email

            if hasattr(user, 'student'):
                initial['phone'] = user.student.tutor_number
            if hasattr(user, 'teacher'):
                initial['phone'] = user.teacher.contact_number     
        return initial



