from django.contrib.auth.models import User
from django.db import models

__author__  = 'ProtocolMapper by Simone Pandolfi'
__email__   = 'simopandolfi@gmail.com'
{% if version is defined %}
__version__ = {{ version }}
{% endif %}

""" This file was generated by ProtocolMapper
    Checkout the repo for more informations [https://github.com/simongsr/protocol_mapper]
"""


{%- macro make_enum(enum) %}
{% for key, value in enum['items'].items() %}
{{ key|upper }} = {{ value|upper }}
{% endfor %}
{{ enum.name|upper }} = (
    {% for key, value in enum['items'].items() %}
    ({{ key|upper }}, {{ value }}),
    {% endfor %}
)
{% endmacro -%}


{%- macro make_model(model) %}
{% if ('python_django__builtin' not in model.modifiers and 'builtin' not in model.modifiers) or model.modifiers.python_django__builtin == False or model.modifiers.builtin == False %}
class {{ model.fullname|join('__') }}(models.Model):
    {% for obj in model.objects.values() if obj.type == 'enum' %}

    {{ make_enum(obj)|indent }}

    {% endfor %}
    {% for field in model.fields.values() if field.id > 0 %}
    {{ field.name }} = {{ field | python_django.field_declaration }}
    {% endfor %}
    {% for field in model.fields.values() if field.id > 0 and field.multiplicity in ('optional', 'required') and field.data_type.type == 'model' %}

    @classmethod
    def get_{{ field.name }}_class(cls):
        return {{ field.data_type.fullname | join('__') }}
    {% endfor %}
    {% for field in model.fields.values() if field.id > 0 and field.multiplicity == 'repeated' and field.data_type is string %}

    @classmethod
    def get_{{ field.name }}_class(cls):
        return __{{ field.model.fullname|join('__') }}___{{ field.name }}
    {% endfor %}

    {% for _model in model|core.nested_models %}

{{ make_model(_model) }}
    {%- endfor %}
    {% for field in model.fields.values() if field.id > 0 and field.multiplicity == 'repeated' and field.data_type is string %}

class __{{ field.model.fullname|join('__') }}___{{ field.name }}(models.Model):
    value = models.{{ field.data_type|python_django.map_data_type }}()
    {% endfor %}
{% endif %}
{% endmacro %}



{% for model in models %}
{{ make_model(model) }}
{% endfor -%}
