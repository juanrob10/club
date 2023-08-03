from django.contrib import admin
from .models import Subject,PackageType,EnrolledPackage,Session,Message
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from django import forms

class SubjectAdmin(admin.ModelAdmin):
    pass

class PackageTypeAdmin(admin.ModelAdmin):
    pass

class MessageAdmin(admin.ModelAdmin):
    pass


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
    readonly_fields = ['session_duration']
    classes=["inline-mod"]
    extra=0

class EnrolledPackageAdmin(ImportExportModelAdmin):
     search_fields = ("student__user__first_name","student__user__last_name","student__user__username")
     inlines = [SessionInline]
     readonly_fields = ['consumed_hours','remaining_hours']
     exclude = ('consumed_time','remaining_time')
  
     
     resource_class = EnrolledPackageResource

class SessionAdmin(admin.ModelAdmin):
    search_fields = ("enrolled_package__student__user__first_name","enrolled_package__student__user__last_name","enrolled_package__student__user__username")
    readonly_fields = ['session_duration']
 

admin.site.register(Subject,SubjectAdmin)
admin.site.register(PackageType,PackageTypeAdmin)
admin.site.register(EnrolledPackage,EnrolledPackageAdmin)
admin.site.register(Session,SessionAdmin)
admin.site.register(Message,MessageAdmin)

