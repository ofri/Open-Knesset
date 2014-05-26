from django import template
register = template.Library()


@register.inclusion_tag('lobbyists/_lobbyists_diff.html')
def lobbyists_diff(lobbyist_history, previous_lobbyist_history):
    (added, deleted) = lobbyist_history.diff(previous_lobbyist_history)
    return {'added': added, 'deleted': deleted}
