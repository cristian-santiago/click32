from django import template

register = template.Library()

@register.filter
def attr(obj, attr_name):
    return getattr(obj, attr_name, None)

@register.filter
def get_field(form, field_name):
    try:
        return form[field_name]
    except KeyError:
        return None

@register.filter
def get_field_url(obj, field_name):
    field = getattr(obj, field_name, None)
    if field and hasattr(field, 'url'):
        return field.url
    return ''

@register.filter
def dict_get(d, key):
    return d.get(key)