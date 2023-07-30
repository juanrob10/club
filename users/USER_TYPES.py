from django.utils.translation import gettext_lazy as _


STUDENT = 1
TEACHER = 2
SUPERVISOR=3

USER_TYPE_CHOICES = (
      (STUDENT, _('student')),
      (TEACHER, _('teacher')),
)