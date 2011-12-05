from django import template
from knesset.okhelptexts.models import Helptext,Keyword

register = template.Library()

@register.inclusion_tag('okhelptexts/okhelptext.html')
def ht(k):
    try:
        oKeyword = Keyword.objects.get(kw_text=k)
        oHelptext = oKeyword.helptext
        res = oHelptext.fulltext
    except Keyword.DoesNotExist: 
        res = 0 
    return {'helptext': res}