from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def add_class(field, css_class):
    """
    Adiciona uma classe CSS a um campo do formulário.
    """
    return field.as_widget(attrs={"class": css_class})
