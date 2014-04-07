from django import template
register = template.Library()


@register.inclusion_tag('lobbyists/_lobbyists_diff.html')
def lobbyists_diff(lobbyist_history):
    lobbyist_history
    return {}
