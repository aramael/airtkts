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

@register.simple_tag
def copy_to_clipboard(text, bgcolour='#ffffff'):
    tpl = get_template('forms/clippy.html')
    return tpl.render(Context({
        'text': text,
        'bgcolour': bgcolour
    }))

@register.assignment_tag
def url_create(request, path):
    return request.build_absolute_uri(path)