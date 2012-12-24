from django import template
from okhelptexts.models import Helptext,Keyword

register = template.Library()

@register.inclusion_tag('okhelptexts/okhelptext.html')
def ht(k):
    try:
        oKeyword = Keyword.objects.get(kw_text=k)
        oHelptext = oKeyword.helptext
        res = oHelptext.fulltext
        moreinfo = oHelptext.moreinfo
    except Keyword.DoesNotExist: 
        return None 
    return {'helptext': res,'moreinfo': moreinfo}
