from django.contrib import admin
from .models import Subject,PackageType,EnrolledPackage,Session,Message,EnrolledPackageSummary
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from .forms import SessionCreateForm,SessionEditForm
from django.utils.html import format_html
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count
from django.db.models.functions import TruncDay,TruncDate, ExtractDay
import json
from django.http import JsonResponse
from django.urls import path

from django.db.models import Count, Case, When, IntegerField, F



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
        
        model = EnrolledPackage
        exclude = ('id','consumed_time','remaining_time')

class SessionInline(admin.TabularInline):

    model =  Session
    form = SessionEditForm
    readonly_fields = ['session_duration']
    classes=["inline-mod"]
    extra=0

class EnrolledPackageAdmin(ImportExportModelAdmin):
    date_hierarchy = "registration_date"


    search_fields = ("student__user__first_name","student__user__last_name","student__user__username")
    inlines = [SessionInline]
    readonly_fields = ['consumed_hours','remaining_hours']
    exclude = ('consumed_time','remaining_time',"id","display_id",)
    list_per_page = 10
    list_display = ("get_student_name","get_package_type","registration_date","status_display",)
    list_filter = ("status",)
    ordering = ("-registration_date",)   

    class Media:
        js = (settings.STATIC_URL + 'js/admin_enrolled_package.js',)
   
    def status_display(self, obj):
        if obj.status:
            return format_html('<span style="color: green;padding-left:10px">&#x2713;</span>')  # Palomita verde
        else:
            return format_html('<span style="color: red;padding-left:10px">&#x2718;</span>')  # Cruz roja
    
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'

    status_display.allow_tags = True        

    def get_package_type(self,obj):   
        return f"{obj.package_type.hours } Hrs" 

    def get_student_name(self, obj):
        return obj.student.user.get_full_name()


    get_package_type.short_description = _("package type")   
    
    get_student_name.admin_order_field = 'student__user__first_name'
    get_student_name.short_description = _("student name")    
     
    resource_class = EnrolledPackageResource
    
   


@admin.register(EnrolledPackageSummary)
class EnrolledPackageSummaryAdmin(admin.ModelAdmin):
    list_filter = ("status",)
    list_per_page = 10
    data_query=None

    change_list_template = 'admin/package_summary_change_list.html' 
    date_hierarchy = "registration_date"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            self.data_query = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            self.data_query = (EnrolledPackage.objects.annotate(date=TruncDay("registration_date"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("-date")
          )

        return response


    def get_urls(self):
        urls = super().get_urls()
        extra_urls = [
            path("chart_data/", self.admin_site.admin_view(self.chart_data_endpoint))
        ]
        # NOTE! Our custom urls have to go before the default urls, because they
        # default ones match anything.
        return extra_urls + urls
    
    def chart_data_endpoint(self,request):
        chart_data = self.chart_data()
        return JsonResponse(chart_data, safe=False)

    def chart_data(self):
        paquetes_date = (
            self.data_query.annotate(date=TruncDay("registration_date"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("-date")
          )
   
        no_paquetes = self.data_query.aggregate(
            active_count=Count(
                Case(When(status=True, then=1), output_field=IntegerField())
            ),
            inactive_count=Count(
                Case(When(status=False, then=1), output_field=IntegerField())
            ),
        )

        chart_data = {
            'paquetes_date': list(paquetes_date),
            'no_paquetes': no_paquetes,
        }
        return chart_data

    def has_add_permission(self, request, obj=None):
        return False  # No permitir la eliminación desde el panel          
    
    def has_delete_permission(self, request, obj=None):
        return False  # No permitir la eliminación desde el panel          
   

       
    def has_change_permission(self, request, obj=None):
        return False  # No permitir la eliminación desde el panel          
   
class SessionAdmin(admin.ModelAdmin):
    list_per_page = 10

    list_display = ("get_student_name","get_teacher_name","get_session_duration","get_date")
    list_filter = ("teacher",)
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
    
    def get_date(self,obj):
        return obj.start_time.strftime("%m/%d/%Y")

    def get_session_duration(self,obj):
        return f"{obj.session_duration } Hrs" 
    
    def get_student_name(self, obj):
        return f"{ obj.enrolled_package.student.user.first_name } {obj.enrolled_package.student.user.last_name}"
    
    def get_teacher_name(self, obj):
        if obj.teacher :
            return f"{ obj.teacher.user.first_name } {obj.teacher.user.last_name}"
        else :
            return  "No teacher"

    get_date.short_description = _("date session")        
    get_student_name.short_description = _("student name",)
    get_teacher_name.short_description = _("teacher name",)
    get_session_duration.short_description = _("session duration")

    get_student_name.admin_order_field = "enrolled_package__student__user__first_name" 
    get_date.admin_order_field = "start_time"


admin.site.register(Subject,SubjectAdmin)
admin.site.register(PackageType,PackageTypeAdmin)
admin.site.register(EnrolledPackage,EnrolledPackageAdmin)
admin.site.register(Session,SessionAdmin)
admin.site.register(Message,MessageAdmin)

