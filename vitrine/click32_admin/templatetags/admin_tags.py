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


@register.filter
def add(value, arg):
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sub(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def split(value, delimiter=' '):
    try:
        return value.split(delimiter)
    except (AttributeError, TypeError):
        return []
    
@register.filter
def sum(value):
    try:
        if isinstance(value, (list, tuple)):
            return sum(float(item) for item in value if item is not None)
        return float(value)
    except (ValueError, TypeError):
        return 0
    
@register.filter
def dictsum(dictionary, index):
    try:
        total = 0
        for key, values in dictionary.items():
            if isinstance(values, list) and index < len(values):
                total += values[index] or 0
        return total
    except:
        return 0

@register.filter
def maxtitle(dictionary, index):
    try:
        max_value = 0
        max_key = 'N/A'
        for key, values in dictionary.items():
            if isinstance(values, list) and index < len(values) and values[index] > max_value:
                max_value = values[index]
                max_key = key.replace('_', ' ').title()
        return max_key
    except:
        return 'N/A'

@register.filter
def zip(list1, list2):
    try:
        return list(zip(list1, list2))
    except (TypeError, AttributeError):
        return []
    
@register.filter
def index(sequence, position):
    """Retorna o item da lista no índice especificado."""
    try:
        return sequence[position]
    except (IndexError, TypeError):
        return None

@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter(name='sum_list')
def sum_list(value):
    try:
        if isinstance(value, (list, tuple)):
            return sum(float(item or 0) for item in value)
        return float(value or 0)
    except (ValueError, TypeError):
        return 0
    
@register.filter
def to_float(value):
    """Converte string com % para float"""
    try:
        if isinstance(value, str):
            value = value.replace('%', '').strip()
        return float(value)
    except (ValueError, TypeError):
        return 0.0
