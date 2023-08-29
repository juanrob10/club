from django.db import models
from users.models import Teacher, Student
from django.utils.html import escape, mark_safe
from django.utils.translation import gettext_lazy as _
import uuid
import datetime
from datetime import timedelta
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django import forms


class Subject(models.Model):
    name = models.CharField(_("name"), max_length=30)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Package Type ID")
    hours = models.IntegerField(_("hours"), default=1)

    class Meta:
        verbose_name = _("package type")
        verbose_name_plural = _("package types")

    def __str__(self):
        return f'{self.hours} Horas'



class EnrolledPackage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Package ID")
    display_id = models.IntegerField(default=1)

    student = models.ForeignKey(Student, verbose_name=_("student"), related_name="enrolled_packages",
                                on_delete=models.CASCADE)
    registration_date = models.DateTimeField(_("registration date"),default=timezone.now)
    consumed_hours = models.CharField(_("consumed hours"), max_length=100, default="00:00:00 Hrs")
    remaining_hours = models.CharField(_("remaining hours"), max_length=100, default="00:00:00 Hrs")

    consumed_time = models.DurationField(_("consumed time"), default=datetime.timedelta(days=0, hours=0, minutes=0))
    remaining_time = models.DurationField(_("remaining_time"), default=datetime.timedelta(days=0, hours=0, minutes=0))

    STATUS_CHOICES = (
        (True, 'Activo'),
        (False, 'Finalizado'))

    package_type = models.ForeignKey('PackageType', verbose_name=_("package type"), on_delete=models.CASCADE,
                                     help_text=_('Select the student package type'), null=True)

    status = models.BooleanField(verbose_name=_("status"), default=True, choices=STATUS_CHOICES,
                                 help_text=_("Select the package status"))

    class Meta:
        verbose_name = _("Enrolled Package")
        verbose_name_plural = _("Enrolled Packages")
        ordering = ['student__user__username', ]

   
    def save(self, edit_from_session=False, *args, **kwargs):
        
        if not edit_from_session:
            time_sesion = timedelta(days=0, hours=0, minutes=0, seconds=0)
            '''
               cuanado agrego mi id( uuid default en el formulario) cuando creo la instancia  enrollPackage mi :
               in self.sessions.all() es:  []
               por eso me permite  intentar iterarla.
               So no lo hiciera no existira esa clave antes antes de guardarla y me tiraria
               un error (no hay clave primaria)


               me quito ese problema solo agregando :  self._state.adding
            '''
            if  self._state.adding:
                # Get the maximum display_id value from the database
                last_id =  EnrolledPackage.objects.all().aggregate(largest=models.Max('display_id'))['largest']

                # aggregate can return None! Check it first.
                # If it isn't none, just use the last ID specified (which should be the greatest) and add one to it
                if last_id is not None:
                    self.display_id = last_id + 1       
            else :
                   for session in self.sessions.all():
                    if session.session_duration is not None:
                        time_sesion += session.session_duration

            self.consumed_time = time_sesion
            m, s = divmod(time_sesion.total_seconds(), 60)
            h, m = divmod(m, 60)
            self.consumed_hours = '{:d}:{:02d}:{:02d} Hrs'.format(int(h), int(m), int(s))

            limite = self.package_type.hours
            limite_timedelta = timedelta(days=0, hours=limite, minutes=0, seconds=0)
            remaining_time = limite_timedelta - time_sesion

            time_0 = timedelta(days=0, hours=0, minutes=0, seconds=0)

            if remaining_time >= time_0:
                self.remaining_time = remaining_time
                m, s = divmod(remaining_time.total_seconds(), 60)
                h, m = divmod(m, 60)
                self.remaining_hours = '{:d}:{:02d}:{:02d} Hrs'.format(int(h), int(m), int(s))

            else:
                self.remaining_time = time_0
                m, s = divmod(time_0.total_seconds(), 60)
                h, m = divmod(m, 60)
                self.remaining_hours = '{:d}:{:02d}:{:02d} Hrs'.format(int(h), int(m), int(s))

            if time_sesion >= timedelta(days=0, hours=limite, minutes=0, seconds=0):
                self.status = False
            else:
                self.status = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.first_name}  {self.student.user.last_name}"

class EnrolledPackageSummary(EnrolledPackage):
    class Meta:
        proxy = True
        verbose_name = _('EnrolledPackage Summary')
        verbose_name_plural = _('EnrolledPackage Summary')

def default_end_time():
    end_time = timezone.now() + timedelta(hours=1)
    return end_time



class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="session ID")
    enrolled_package = models.ForeignKey(EnrolledPackage, verbose_name=_("enrolled package"), related_name="sessions",
                                         on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, related_name="sessions", verbose_name=_("teacher"), on_delete=models.SET_NULL,
                                null=True)
    subjects = models.ManyToManyField(Subject, verbose_name=_("subjects"), related_name='sessions')

    start_time = models.DateTimeField(verbose_name=_("start time"), null=False, blank=False,default=timezone.now)
    end_time = models.DateTimeField(null=True, verbose_name=_("end time"), blank=True,default=default_end_time)
    session_duration = models.DurationField(_("session duration"), null=True, blank=True)

    class Meta:
        verbose_name = _("Session")
        verbose_name_plural = _("Sessions")
        ordering = ['-start_time']

    def __str__(self):
        enrolled_package = getattr(self, 'enrolled_package', None)
        if enrolled_package :
            return self.enrolled_package.student.user.get_full_name()
            
        return "Enrolled Package Not Available"

class Message(models.Model):
    name = models.CharField(_("name"), max_length=100)
    email = models.EmailField(blank=True, null=True)
    concern = models.CharField(_("concern"), max_length=200)
    message = models.TextField(verbose_name=_("note"))
    phone = PhoneNumberField(verbose_name=_("phone"), blank=True, null=True)  # Campo opcional y puede estar vacío

    def __str__(self):
        return self.concern

    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
