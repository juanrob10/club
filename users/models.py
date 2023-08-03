from django.contrib.auth.base_user import AbstractBaseUser,BaseUserManager
from django.contrib.auth.models import PermissionsMixin,AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from PIL import Image
from .USER_TYPES import USER_TYPE_CHOICES,STUDENT,TEACHER
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
from django.conf import settings
import os

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, username,email,first_name,last_name, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not username:
            raise ValueError(_("The Username must be set"))
        if not email:
            raise ValueError(_("The Email must be set"))
        if not first_name:
            raise ValueError(_("The First name must be set"))
        if not last_name:
            raise ValueError(_("The Last name must be set"))
        
        email = self.normalize_email(email)
        user = self.model(username=username,email=email,first_name=first_name,last_name=last_name,**extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self,username,email,first_name,last_name, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
  
        extra_fields.setdefault("user_type", TEACHER)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        
        return self.create_user(username,email,first_name,last_name,password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_("email address"), blank=True,null=True)
    first_name = models.CharField(_("first name"), max_length=150, blank=False)
    last_name = models.CharField(_("last name"), max_length=150, blank=False)
    user_type = models.PositiveSmallIntegerField(_("user type"),default=STUDENT,choices=USER_TYPE_CHOICES,null=True)
  
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email","first_name","last_name"]

    

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.first_name

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
    def __str__(self):
        return self.get_full_name()
    
class Student(models.Model):
    user = models.OneToOneField(CustomUser,verbose_name=CustomUser._meta.verbose_name,related_name="student", on_delete=models.CASCADE, primary_key=True) 
    picture = models.ImageField(_("picture"),default="default.jpg",upload_to="profile_pics")
    date_birth= models.DateField(verbose_name=_("date birth"),blank=True, null=True)

    tutor_name =  models.CharField(verbose_name=_("tutor name"),max_length=100,blank=True)
    tutor_number  = PhoneNumberField(verbose_name=_("tutor number"),blank=True)

    class Meta:
        verbose_name = _("student")
        verbose_name_plural = _("students")

    def __str__(self):
        return self.user.get_full_name()
    


    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)   
        if self.picture:
            img = Image.open(self.picture.path)
            if img.height > 300 or img.width >300:
                outputsize =(300,300)
                img.thumbnail(outputsize)
                img.save(self.picture.path)  
                 

        

    
class Teacher(models.Model):
    user = models.OneToOneField(CustomUser,verbose_name=CustomUser._meta.verbose_name,related_name="teacher", on_delete=models.CASCADE, primary_key=True)
    contact_number  = PhoneNumberField(verbose_name=_("conact number"),blank=True)
   
    class Meta:
        verbose_name = _("teacher")
        verbose_name_plural = _("teachers")
  
    def __str__(self):
        return self.user.username




