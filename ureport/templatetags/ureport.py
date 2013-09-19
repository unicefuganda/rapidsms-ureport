from django import template

from django.template import Node, resolve_variable,Variable
from django.conf import settings

register = template.Library()

class SetVarNode(template.Node):

    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value

    def render(self, context):
        try:
            value = template.Variable(self.var_value).resolve(context)
        except template.VariableDoesNotExist:
            value = ""
        context[self.var_name] = value
        return u""


def set_var(parser, token):
    """
        {% set <var_name>  = <var_value> %}
    """
    parts = token.split_contents()
    if len(parts) < 4:
        raise template.TemplateSyntaxError("'set' tag must be of the form:  {% set <var_name>  = <var_value> %}")
    return SetVarNode(parts[1], parts[3])


class AddGetParameter(Node):
    def __init__(self, values):
        self.values = values

    def render(self, context):
        req = resolve_variable('request',context)
        params = req.GET.copy()
        for key, value in self.values.items():
            params[key] = Variable(value).resolve(context)
        return '?%s' %  params.urlencode()


@register.tag
def add_get_parameter(parser, token):
    """
    {% load add_get_parameter %}
    <a href="{% add_get_paramater param1='const_value',param2=variable_in_context %}">
    Link with modified params
     for instances when u want to search and paginate
    </a>
    """
    from re import split
    contents = split(r'\s+', token.contents, 2)[1]
    pairs = split(r',', contents)

    values = {}

    for pair in pairs:
        s = split(r'=', pair, 2)
        values[s[0]] = s[1]

    return AddGetParameter(values)

@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

register.tag('set', set_var)


@register.filter
def cap_slugify(value):
    return value.replace(" ", "_").replace("/", " ")
