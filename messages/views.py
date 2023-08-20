from django.shortcuts import render

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