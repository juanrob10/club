from django.db import models
from users.models import Teacher,Student
from django.utils.html import escape, mark_safe
from django.utils.translation import gettext_lazy as _
import uuid
import datetime
from datetime import timedelta
from phonenumber_field.modelfields import PhoneNumberField

class Subject(models.Model):
    name = models.CharField(_("name"),max_length=30)
    color = models.CharField(max_length=7, default='#007bff')

    class Meta:
        verbose_name = _("subject")
        verbose_name_plural = _("subjects")

    def __str__(self):
        return self.name

    def get_html_badge(self):
        name = escape(self.name)
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (color, name)
        return mark_safe(html)
    

class PackageType(models.Model):
    hours = models.IntegerField(_("hours"),default=1)

    class Meta:
        verbose_name = _("package type")
        verbose_name_plural = _("package types")

    def __str__(self):
        return f'{self.hours} Horas'

class EnrolledPackage(models.Model):
     id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Package ID")
     student = models.ForeignKey(Student,verbose_name=_("student"),related_name="enrolled_packages",on_delete=models.CASCADE)
     registration_date  = models.DateField(_("registration date"),null=True,blank=True)
     consumed_hours = models.CharField(_("consumed hours"),max_length=100,default="00:00:00 Hrs")
     remaining_hours = models.CharField(_("remaining hours"),max_length=100,default="00:00:00 Hrs")
   
     consumed_time= models.DurationField(_("consumed time"),default=datetime.timedelta(days=0,hours=0,minutes=0))
     remaining_time = models.DurationField(_("remaining_time"),default=datetime.timedelta(days=0,hours=0,minutes=0))

     STATUS_CHOICES =(
     (True,'Activo'),
     (False,'Finalizado'))

     package_type  = models.ForeignKey('PackageType',verbose_name="package type",on_delete=models.CASCADE,help_text=_('Select the student package type'),null=True)

     status = models.BooleanField(verbose_name=_("status"),default=True,choices=STATUS_CHOICES,help_text=_("Select the package status"))

     class Meta:
        verbose_name = _("Enrolled Package")
        verbose_name_plural = _("Enrolled Packages")
        ordering = ['student__user__username',]

     def save(self,edit_from_session=False,*args,**kwargs):
        if  not edit_from_session:
             time_sesion = timedelta(days=0, hours=0, minutes=0, seconds=0)
             for session in self.sessions.all():
                    if session.session_duration is not None:
                        time_sesion += session.session_duration
                        
             self.consumed_time = time_sesion
             m, s = divmod(time_sesion.total_seconds(), 60)
             h, m = divmod(m, 60)
             self.consumed_hours = '{:d}:{:02d}:{:02d} Hrs'.format(int(h),int(m),int(s))
            
             limite = self.package_type.hours
             limite_timedelta =  timedelta(days=0,hours=limite,minutes=0,seconds=0)
             remaining_time = limite_timedelta - time_sesion
                
             time_0 = timedelta(days=0,hours=0,minutes=0,seconds=0)

             if remaining_time >= time_0:
                    self.remaining_time = remaining_time
                    m, s = divmod(remaining_time.total_seconds(), 60)
                    h, m = divmod(m, 60)
                    self.remaining_hours  = '{:d}:{:02d}:{:02d} Hrs'.format(int(h),int(m),int(s))
                
             else:
                    self.remaining_time = time_0
                    m, s = divmod(time_0.total_seconds(), 60)
                    h, m = divmod(m, 60)
                    self.remaining_hours = '{:d}:{:02d}:{:02d} Hrs'.format(int(h),int(m),int(s))
                
             if time_sesion >= timedelta(days=0,hours=limite,minutes=0,seconds=0):
                    self.status = False 
             else:
                    self.status = True            
        super().save(*args,**kwargs)    


     def __str__(self):
        if self.status:
            return  f"{self.student.user.first_name}  {self.student.user.last_name} (Status: ACTIVO)"
        else:
            return  f"{self.student.user.first_name}  {self.student.user.last_name} (Status: FINALIZADO)"  
     
               
class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="session ID")
    enrolled_package = models.ForeignKey(EnrolledPackage,verbose_name=_("enrolled package"), related_name="sessions", on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, related_name="sessions", verbose_name=_("teacher"),on_delete=models.SET_NULL,null=True)
    subjects = models.ManyToManyField(Subject, verbose_name=_("subjects"), related_name='sessions')

    start_time = models.DateTimeField(verbose_name=_("start time"),null=False, blank=False)
    end_time = models.DateTimeField(null=True,verbose_name=_("end time"), blank=True)
    session_duration = models.DurationField(_("session duration"), null=True, blank=True)
    observations = models.TextField(_("observations"), blank=True)

    class Meta:
        verbose_name = _("Session")
        verbose_name_plural = _("Sessions")
        ordering = ['-start_time']

    def __str__(self):
        if self.subjects:
            class_subjects = []
            for subject in self.subjects.all():
                class_subjects.append(subject.name)
            string_classes =  ','.join(class_subjects)    

            if self.session_duration:
                return f'({self.enrolled_package.student.user.get_full_name()}) materias: {string_classes}: duracion: {self.session_duration} Hrs'
            else :
                return f'{self.enrolled_package.student.user.get_full_name()} materias:{string_classes}: duracion: Por definir'
        return self.enrolled_package.student.user.get_full_name()
    
   
class Message(models.Model):
    name = models.CharField(_("name"),max_length=100)
    email = models.EmailField(blank=True, null=True)
    concern = models.CharField(_("concern"),max_length=200)
    message = models.TextField(_("message"))
    phone = PhoneNumberField(_("phone"),blank=True, null=True)  # Campo opcional y puede estar vacío

    def __str__(self):
        return self.concern

    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
