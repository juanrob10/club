from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Student, Teacher
from school.models import  EnrolledPackage
from .forms import StudentForm,TeacherForm,CustomUserChangeForm,CustomUserCreationForm
from django.utils.html import escape, mark_safe
from django.utils.translation import gettext_lazy as _

from .USER_TYPES import STUDENT,TEACHER
from PIL import Image




class EnrolledPackageInline(admin.TabularInline):
    model =  EnrolledPackage
    readonly_fields = ['consumed_hours','remaining_hours']
    exclude = ('consumed_time','remaining_time',)
    classes=["inline-mod"]
    extra=0




class CustomUserAdmin(UserAdmin):
    #form = CustomUserChangeForm
    #add_form = CustomUserCreationForm
    
    model = CustomUser
    list_display = ("first_name","is_staff", "is_active","is_superuser")
    list_filter = ("username","first_name","last_name", "is_staff", "is_active",)
    fieldsets = (
        (None, {"fields": ("username","first_name",'last_name',"email","user_type", "password",)}),
        ("Fechas importantes",{"fields": ("last_login","date_joined")}),
        ("Permisos", {"fields": ("is_staff","is_superuser", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username","email","first_name","last_name","user_type", "password1", "password2", "is_staff",
                "is_active","is_superuser", "groups", "user_permissions"
            )}
        ),
    )
    def nombre(self,obj):
        return obj.get_full_name()

    readonly_fields = ['date_joined','last_login']
    search_fields = ("email",)
    ordering = ("email",)
     
        
   
class StudentAdmin(admin.ModelAdmin):
    form = StudentForm
    
    list_display = ("get_name","get_username")
    list_filter = ("user__first_name","user__last_name","user__username")
    search_fields = ("user__first_name","user__last_name","user__username",)

    fieldsets = (
        (None, {"fields": ("user","picture","vista_previa","date_birth","tutor_name","tutor_number",)}),)

    inlines = [EnrolledPackageInline]
    readonly_fields = ['vista_previa']

    def vista_previa(self, obj):
        return mark_safe('<img src="{url}" width="{width}" height={height} />'.format(
            url = obj.picture.url,
            width=obj.picture.width,
            height=obj.picture.height,
            )
    )

    def get_username(self,obj):
        return obj.user.username

    def get_name(self,obj):
        return  obj.user.get_full_name()
  
        # Sobrescribe el método has_delete_permission para profesores
        
    def has_add_permission(self, request, obj=None):
        return False  # No permitir la eliminación desde el panel          

    get_name.short_description = _("name")  
    get_username.short_description = _("username")

  


class TeacherAdmin(admin.ModelAdmin):
    list_display = ("get_username","get_name",)

    form = TeacherForm

    def get_username(self,obj):
        return obj.user.username

    def get_name(self,obj):
        return  obj.user.get_full_name()  

    # Sobrescribe el método has_delete_permission para profesores
    def has_add_permission(self, request, obj=None):
        return False  # No permitir la eliminación desde el panel    

    get_name.short_description = _("name")  
    get_username.short_description = _("username")      

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Student,StudentAdmin)
admin.site.register(Teacher,TeacherAdmin)