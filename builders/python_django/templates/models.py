import json

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
{% for _model in model|core.nested_models %}

{{ make_model(_model) }}
{%- endfor %}
{% for field in model.fields.values() if field.id > 0 and field.multiplicity == 'repeated' and field.data_type is string %}

class {{ field.model.fullname|join('') }}{{ field.name }}(models.Model):
    value = models.{{ field.data_type|python_django.map_data_type }}({{ field.modifiers|python_django.prepare_args|join(', ') }})

    def __str__(self):
        return '{{ field.model.fullname|join("") }}{{ field.name }}: {0}'.format(self.id)

{% endfor %}
{% if ('python_django__builtin' not in model.modifiers and 'builtin' not in model.modifiers) or model.modifiers.python_django__builtin == False or model.modifiers.builtin == False %}
class {{ model.fullname|join('_') }}(models.Model):
    {% for obj in model.objects.values() if obj.type == 'enum' %}

    {{ make_enum(obj)|indent }}

    {% endfor %}
    {% for field in model.fields.values() if field.id > 0 %}
    {{ field.name }} = {{ field|python_django.field_declaration }}
    {% endfor %}

    def __str__(self):
        return '{{ model.fullname|join("_") }}: {0}'.format(self.id)

    {% for field in model.fields.values() if field.id > 0 and field.multiplicity in ('optional', 'required') and field.data_type.type == 'model' %}
    @classmethod
    def get_{{ field.name }}_class(cls):
        return {{ field.data_type.fullname|join('_') }}
    {% endfor %}
    {% for field in model.fields.values() if field.id > 0 and field.multiplicity == 'repeated' and field.data_type is string %}

    @classmethod
    def get_{{ field.name }}_class(cls):
        return {{ field.model.fullname|join('') }}{{ field.name }}
    {% endfor %}
{% endif %}

{% endmacro -%}


{%- macro make_message(message) %}
{% for _message in message | core.nested_messages %}
{{ make_message(_message) }}

{%- endfor %}
class {{ message.fullname|join('__') }}:
    def __init__(self):
        {% for field in message.fields.values() %}
            {% set value = None %}
            {% if field.multiplicity == 'repeated' %}
                {% set value = [] %}
            {% endif %}
            {% set default_value = None %}
            {% if field.data_type is not mapping %}
                {% if field.multiplicity == 'repeated' %}
                    {% set initial_value = [] %}
                {% elif field.multiplicity == 'optional' %}
                    {% if 'default' in field.modifiers %}
                        {% set default_value = field.modifiers['default'] %}
                    {% else %}
                        {% set default_value = (field.data_type|core.map_default_value)() %}
                    {% endif %}
                {% endif %}
            {% endif %}
            {% set required = False %}
            {% if field.multiplicity == 'required' %}
                {% set required = True %}
            {% endif %}
            {% set type = field['data_type'] %}
            {% if type is mapping %}
                {% set type = type.fullname|join('__') %}
            {% endif %}
        self.__{{ field.name }} = {'initialized': False, 'value': {{ value }}, 'default_value': {{ default_value }}, 'required': {{ required }}, 'type': {{ type }}}
        {% endfor %}

    {% for field in message.fields.values() %}
    @property
    def {{field.name}}(self):
        if not self.__{{ field.name }}['required'] and not self.__{{ field.name }}['initialized']:
            return self.__{{ field.name }}['default_value']
        return self.__{{ field.name }}['value']

    {%  if field.multiplicity != 'repeated' %}
    @{{ field.name }}.setter
    def {{ field.name }}(self, value):
        if not isinstance(value, {{ field.data_type|python.map_data_type }}):
            raise TypeError("Expected '{{ field.name }}' is a {{ field.data_type|python.map_data_type }}, got: {0}".format(type(value).__name__))
        self.__{{ field.name }}['value'] = value
        self.__{{ field.name }}['initialized'] = True
    {% else %}
    @{{field.name}}.setter
    def {{ field.name }}(self, value):
        if not hasattr(value, '__iter__') or not callable(value.__iter__):
            raise Exception("Value must be an instance of iterable, got: {0}".format(type(value).__name__))
        for arg in value:
            if not isinstance(arg, {{ field.data_type|python.map_data_type }}):
                raise TypeError("Expected '{{ field.name }}' is a {{ field.data_type|python.map_data_type }}, got: {0}".format(type(arg).__name__))
        self.__{{ field.name }}['value'] = []
        self.add_{{ field.name }}(*value)

    def add_{{ field.name }}(self, *args):
        for arg in args:
            if not isinstance(arg, {{ field.data_type|python.map_data_type }}):
                raise TypeError("Expected '{{ field.name }}' is a {{ field.data_type|python.map_data_type }}, got: {0}".format(type(arg).__name__))
        self.__{{ field.name }}['value'] += list(args)
        self.__{{ field.name }}['initialized'] = True

    def del_{{ field.name }}(self, *args):
        """ Removes all occurrences of the items. """
        for arg in args:
            try:
                while True:
                    self.__{{ field.name }}['value'].remove(arg)
            except ValueError:
                pass
    {% endif %}

    {% endfor %}
    {% for modelname, fieldlist in (message|core.map_message_field_to_model).items() %}
    def put_{{ modelname|replace('.', '__') }}(self, model):
        if not isinstance(model, {{ modelname|replace('.', '__') }}):
            raise TypeError("Model must be an instance of {{ modelname|replace('.', '__') }}, got: {0}".format(type(model).__name__))
        {% for field in fieldlist %}
            {% if field.multiplicity != 'repeated' %}
        self.{{ field.name }} = model.{{ field.model_field.name }}
            {% else %}
        self.{{ field.name }} = [item for item in model.{{ field.model_field.name }}.all()]
            {% endif %}
        {% endfor %}

    {% endfor %}
    def dump(self):
        {% for field in message.fields.values() if field.multiplicity == 'required' %}
        if not self.__{{ field.name }}['initialized']:
            raise Exception("Could not serialize '{{ message.fullname|join('.') }}', '{{ field.name }}' has not been initialized!")
        {% endfor %}
        return json.dumps({
            {% for field in message.fields.values() %}
                {% if field.data_type is mapping %}
            '{{ field.name }}': self.{{ field.name }}.dump(),
                {% else %}
            '{{ field.name }}': self.{{ field.name }},
                {% endif %}
            {% endfor %}
        })

    @classmethod
    def load(cls, data):
        obj = json.loads(data)
        new_instance = cls()
        {% for field in message.fields.values() %}
            {% if field.data_type is mapping %}
                {% if field.multiplicity == 'repeated'%}
        new_instance.{{ field.name }} = [{{ field.data_type|python.map_data_type }}.load(item) for item in obj['{{ field.name }}']]
                {% else %}
        new_instance.{{ field.name }} = {{ field.data_type|python.map_data_type }}.load(obj['{{ field.name }}'])
                {% endif %}
            {% else %}
        new_instance.{{ field.name }} = obj['{{ field.name }}']
            {% endif %}
        {% endfor %}

{% endmacro %}



{% for model in models %}
{{ make_model(model) }}
{% endfor -%}

{% for message in messages %}
{{ make_message(message) }}
{% endfor %}
