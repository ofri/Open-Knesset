from django import template
register = template.Library()

@register.inclusion_tag('committees/_meeting_li.html')
def committee_meeting_list_item(cm):
    return {'o': cm}
