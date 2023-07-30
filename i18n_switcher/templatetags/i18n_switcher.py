from django import template
from django.template.defaultfilters import stringfilter
from core.urls  import urlpatterns


from django.conf import settings
 
def switch_lang_code(path, language):
   
    # Get the supported language codes
    lang_codes = [c for (c, name) in settings.LANGUAGES]
    
    # Validate the inputs
    if path == '':
        raise Exception('URL path for language switch is empty')
    elif path[0] != '/':
        raise Exception('URL path for language switch does not start with "/"')
    elif language not in lang_codes:
        raise Exception('%s is not a supported language code' % language)
    
    if (not urlpatterns[0].pattern.prefix_default_language and language == settings.LANGUAGE_CODE):
        return "/admin/"
    else:
        return f"/{language}/admin"

register = template.Library()

@register.filter
def switch_i18n(request, language):
    """takes in a request object and gets the path from it"""
    return switch_lang_code(request.get_full_path(), language)