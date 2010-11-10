from django import template
from django.core import urlresolvers
from django.conf import settings
from knesset.auxiliary.forms import SearchForm

register = template.Library()

@register.inclusion_tag('search/search_form.html', takes_context=True)
def search_form(context, search_form_id='search'):
    request = context['request']
    auto_id = 'id_%s_%%s' % search_form_id
    return {
        'form': SearchForm(initial=request.GET, auto_id=auto_id),
        'search_form_id': search_form_id,
        'action': urlresolvers.reverse('site-search'),
        'lang': 'he',
        'cx' : settings.GOOGLE_CUSTOM_SEARCH
    }
