from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.class Message(models.Model):
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

