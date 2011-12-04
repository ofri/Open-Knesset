from django import template

register = template.Library()

@register.inclusion_tag('laws/bill_full_name.html')
def bill_full_name(bill):
    return { 'bill': bill }

@register.inclusion_tag('laws/bill_list_item.html')
def bill_list_item(bill):
    return { 'bill': bill }

@register.inclusion_tag('laws/item_tags.html')
def item_tags(tags):
    return { 'tags': tags }

@register.inclusion_tag('laws/bill_inabox.html')
def bill_inabox(bill):
    return { 'bill': bill }
