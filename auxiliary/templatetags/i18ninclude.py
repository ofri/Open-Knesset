import os
from django import template
register = template.Library()

@register.simple_tag
def i18ninclude(template_name, language):
    template_name, extension = os.path.splitext(template_name)
    template_name = '%s.%s%s' % (template_name, language, extension)
    return template.loader.render_to_string(template_name)

