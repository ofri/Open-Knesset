from django import template
from django.utils.translation import ugettext as _

register = template.Library()


@register.inclusion_tag('auxiliary/_bar.html')
def bar(quantity, start, end, bar_class=None, show_label=True):
    """
    Draws a bar.

    :param quantity: The quantity to represent
    :param start: Start of scale
    :param end: End of scale
    :param bar_class: Bootstrap bar class (One of: info, success, warning,
                      danger). If not passed, will be calculated from percentage
    :param show_label: Show the descriptive label ?
    """

    assert quantity <= end, "bar: quantity > end"

    try:
        value = (quantity - start) * 100 / (end - start)
    except (TypeError, ZeroDivisionError):
        return {'applicable': False}

    VALUES = (
        (20, 'danger', _('Extremely below average')),
        (40, 'warning', _('Below average')),
        (60, 'info', _('Average')),
        (80, 'info', _('Above average')),
        (101, 'success', _('Extremely above average')),
    )

    for boundary, css_class, label in VALUES:
        if value < boundary:
            break

    if not bar_class:
        bar_class = css_class

    if not show_label:
        label = ''

    return {'width': value, 'bar_class': bar_class, 'label': label,
            'quantity': quantity, 'applicable': True}
