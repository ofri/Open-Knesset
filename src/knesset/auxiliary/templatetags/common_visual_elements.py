from django import template

register = template.Library()

@register.inclusion_tag('auxiliary/_bar.html')
def bar(weight, bar_class, norm_factor=1.2, baseline=0):
    """ Draws a bar.
        weight - translates to bar length
        bar_class - class attribute of the bar element, used for css capture
    """
    if not weight:
        weight = 0
    weight=abs(weight)
    if norm_factor:
        width = round((weight-baseline)/norm_factor,1)
    else:
        width = 0
    return {'width': width, 'bar_class':bar_class}

