from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class MessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messages'
    verbose_name = _('messages')
