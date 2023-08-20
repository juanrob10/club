from django.contrib import admin
from .models import Subject,PackageType,EnrolledPackage,Session,Message
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .forms import SessionCreateForm,SessionEditForm
from django.utils.html import format_html

from django.conf import settings

from django.utils.translation import gettext_lazy as _
from django.db import models

class SubjectAdmin(admin.ModelAdmin):
    pass

class PackageTypeAdmin(admin.ModelAdmin):
    pass

class MessageAdmin(admin.ModelAdmin):
    list_display = ("name","concern",)


class EnrolledPackageResource(resources.ModelResource):
    
    # Specify the fields to include in the import/export
    student = fields.Field(attribute='student',column_name="Estudiante")
    package_type = fields.Field(attribute='package_type',column_name="Tipo de Paquete")
    registration_date = fields.Field(attribute='registration_date',column_name="Fecha de Registro")
    consumed_hours = fields.Field(attribute='consumed_hours',column_name="Horas Cosumidas")
    remaining_hours = fields.Field(attribute='remaining_hours',column_name="Horas Restantes")
 
    status = fields.Field(column_name='Estado')

    def dehydrate_status(self, obj):
        # Define la lógica para el valor de la columna virtual 'status'
        if obj.status:
            return 'Activo'
        else:
            return 'Finalizado'
        

    class Meta:
        model = EnrolledPackage
        exclude = ('id','consumed_time','remaining_time')  
     
class SessionInline(admin.TabularInline):

    model =  Session
    form = SessionEditForm
    readonly_fields = ['session_duration']
    classes=["inline-mod"]
    extra=0

class EnrolledPackageAdmin(ImportExportModelAdmin):
    list_per_page = 50
    list_display = ("get_student_name","get_package_type","registration_date","status_display",)
    
    class Media:
        js = (settings.STATIC_URL + 'js/admin_enrolled_package.js',)
   
    def status_display(self, obj):
        if obj.status:
            return format_html('<span style="color: green;padding-left:10px">&#x2713;</span>')  # Palomita verde
        else:
            return format_html('<span style="color: red;padding-left:10px">&#x2718;</span>')  # Cruz roja
    
    status_display.short_description = 'Status'
    status_display.allow_tags = True        


    def get_package_type(self,obj):
              
        return f"{obj.package_type.hours } Hrs" 


    def get_student_name(self, obj):
        return obj.student.user.get_full_name()


    get_package_type.short_description = _("package type")   
    
    get_student_name.admin_order_field = 'student__user__first_name'
    get_student_name.short_description = _("student name")    
    
    search_fields = ("student__user__first_name","student__user__last_name","student__user__username")
    inlines = [SessionInline]
    readonly_fields = ['consumed_hours','remaining_hours']
    exclude = ('consumed_time','remaining_time',"id",)
   
     
    resource_class = EnrolledPackageResource

class SessionAdmin(admin.ModelAdmin):
    list_per_page = 10

    list_display = ("get_student_name","get_teacher_name","session_date","get_session_duration")
  
    search_fields = ("enrolled_package__student__user__first_name","enrolled_package__student__user__last_name","enrolled_package__student__user__username")
    readonly_fields = ['session_duration']
    exclude = ('id',)

    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if obj is None:
            defaults['form'] = SessionCreateForm
        else :
            defaults['form'] = SessionEditForm
               
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)
    

    def get_session_duration(self,obj):
        return f"{obj.session_duration } Hrs" 
    
    def get_student_name(self, obj):
        return f"{ obj.enrolled_package.student.user.first_name } {obj.enrolled_package.student.user.last_name}"
    
    def get_teacher_name(self, obj):
        if obj.teacher :
            return f"{ obj.teacher.user.first_name } {obj.teacher.user.last_name}"
        else :
            return  "No teacher"
            
    get_student_name.short_description = _("student name",)
    get_teacher_name.short_description = _("teacher name",)
    get_session_duration.short_description = _("session duration")


admin.site.register(Subject,SubjectAdmin)
admin.site.register(PackageType,PackageTypeAdmin)
admin.site.register(EnrolledPackage,EnrolledPackageAdmin)
admin.site.register(Session,SessionAdmin)
admin.site.register(Message,MessageAdmin)

