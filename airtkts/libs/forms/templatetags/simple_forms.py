from django.template import Library
from django.template.loader import get_template
from django.template.context import Context

register = Library()

@register.simple_tag
def bootstrap_horizontal_field(field):
    tpl = get_template('forms/bootstrap_horizontal_field.html')
    return tpl.render(Context({
        'field': field
    }))

@register.simple_tag
def bootstrap_field(field):
    tpl = get_template('forms/bootstrap_basic_field.html')
    return tpl.render(Context({
        'field': field
    }))