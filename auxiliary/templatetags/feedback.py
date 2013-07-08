from django import template

from auxiliary.forms import FeedbackSuggestionForm

register = template.Library()


class FeedbackFormNode(template.Node):
    "Addes the feedback suggestion for into context"

    def render(self, context):
        forms = context.get('suggestion_forms', {})
        forms['feedback'] = FeedbackSuggestionForm()
        context['suggestion_forms'] = forms
        return ''


def do_add_feedback_suggestion_form(parser, token):
    return FeedbackFormNode()


register.tag('add_feedback_suggestion_form', do_add_feedback_suggestion_form)
