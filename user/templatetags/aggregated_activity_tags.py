from django.template import Variable, Library, Node, TemplateSyntaxError, TemplateDoesNotExist
from django.template.loader import render_to_string

class DisplayAggregatedAction(Node):
    def __init__(self, aggr_action, varname=None):
        self.aggr_action = Variable(aggr_action)
        self.varname = varname
        
    def render(self, context):
        aggr_action_instance = self.aggr_action.resolve(context)
        try:
            aggr_action_output = render_to_string(('activity_aggr/%(verb)s/aggr_action.html' % { 'verb':aggr_action_instance.verb.replace(' ','_') }),{ 'aggr_action':aggr_action_instance },context)
        except TemplateDoesNotExist:
            aggr_action_output = render_to_string(('activity_aggr/aggr_action.html'),{ 'aggr_action':aggr_action_instance },context)
        if self.varname is not None:
            context[self.varname] = aggr_action_output
            return ""
        else:
            return aggr_action_output 

def do_print_aggregated_action(parser, token):
    bits = token.contents.split()
    if len(bits) > 3:
        if len(bits) != 4:
            raise TemplateSyntaxError, "Accepted formats {% display_aggregated_action [aggr_action] %} or {% display_aggregated_action [aggr_action] as [var] %}"
        if bits[2] != 'as':
            raise TemplateSyntaxError, "Accepted formats {% display_aggregated_action [aggr_action] %} or {% display_aggregated_action [aggr_action] as [var] %}"
        return DisplayAggregatedAction(bits[1],bits[3])
    else:
        return DisplayAggregatedAction(bits[1])
    
register = Library()     
register.tag('display_aggr_action', do_print_aggregated_action)
 