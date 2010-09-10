from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='pretty_crop')
@stringfilter
def pretty_crop(text, length):
    """ Crops text after whole words.
        text - text to crop
        length - maximum length of cropped text
    """
    
    if not text:
        return ""
    
    if type(text) not in [str,unicode]:
        text = unicode(text)
    
    if len(text)<=length:
        return text
    
    last_allowed_space_location = text[0:length].rfind(' ') 
    return text[0:last_allowed_space_location]+'...'

