from django import template
register = template.Library()


@register.inclusion_tag('committees/_meeting_li.html')
def committee_meeting_list_item(cm, add_li=True, show_committee_name=False, show_present=False):
    return {'o': cm,
            'add_li': add_li,
            'show_committee_name': show_committee_name,
            'show_present': show_present,
           }
