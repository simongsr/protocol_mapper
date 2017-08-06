{%- macro make_message(message) %}
{% for _message in message|core.nested_messages %}
{{ make_message(_message) }}

{%- endfor %}
class {{ message|python_django.class_name }}:
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
                {% set type = type|python_django.class_name %}
            {% endif %}
        self.__{{ field.name }} = {
            'initialized'  : False,
            'value'        : {{ value }},
            'default_value': {{ default_value }},
            'required'     : {{ required }},
            'type'         : {{ type }}
        }
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
        {% if field.data_type is string %}
        if not isinstance(value, {{ field.data_type|python.map_data_type }}):
            raise TypeError(
                "Expected '{{ field.name }}' is a {{ field.data_type|python.map_data_type }}, got: {0}".format(
                    type(value).__name__))
        {% else %}
        if not isinstance(value, {{ field|python_django.class_name }}):
            raise TypeError(
                "Expected '{{ field.name }}' is a {{ field|python_django.class_name }}, got: {0}".format(
                    type(value).__name__))
        {% endif %}
        self.__{{ field.name }}['value'] = value
        self.__{{ field.name }}['initialized'] = True
    {% else %}
    @{{field.name}}.setter
    def {{ field.name }}(self, value):
        if not hasattr(value, '__iter__') or not callable(value.__iter__):
            raise Exception("Value must be an instance of iterable, got: {0}".format(type(value).__name__))
        for arg in value:
            {% if field.data_type is string %}
            if not isinstance(value, {{field.data_type|python.map_data_type}}):
                raise TypeError(
                    "Expected '{{ field.name }}' is a {{ field.data_type|python.map_data_type }}, got: {0}".format(
                        type(value).__name__))
            {% else %}
            if not isinstance(value, {{field|python_django.class_name}}):
                raise TypeError(
                    "Expected '{{ field.name }}' is a {{ field|python_django.class_name }}, got: {0}".format(
                        type(value).__name__))
            {% endif %}
        self.__{{ field.name }}['value'] = []
        self.add_{{ field.name }}(*value)

    def add_{{ field.name }}(self, *args):
        for arg in args:
            {% if field.data_type is string %}
            if not isinstance(arg, {{field.data_type | python.map_data_type}}):
                raise TypeError(
                    "Expected '{{ field.name }}' is a {{ field.data_type|python.map_data_type }}, got: {0}".format(
                        type(arg).__name__))
            {% else %}
            if not isinstance(arg, {{field | python_django.class_name}}):
                raise TypeError(
                    "Expected '{{ field.name }}' is a {{ field|python_django.class_name }}, got: {0}".format(
                        type(arg).__name__))
            {% endif %}
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
    def put_{{ modelname|core.upper_camel_case }}(self, model):
        if not isinstance(model, {{ modelname|core.upper_camel_case }}):
            raise TypeError(
                "Model must be an instance of {{ modelname|core.upper_camel_case }}, got: {0}".format(
                    type(model).__name__))
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
            raise Exception(
                "Could not serialize '{{ message.fullname|join('.') }}', '{{ field.name }}' has not been initialized!")
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
    def load(cls, obj, parse=True):
        if not isinstance(parse, bool):
            raise TypeError('Parse must be a boolean, got: {0}'.format(type(obj).__name__))
        if parse:
            obj = json.loads(obj)
        new_instance = cls()
        {% for field in message.fields.values() %}
            {% if field.data_type is mapping %}
                {% if field.multiplicity != 'repeated'%}
                    {% if field.data_type is string %}
        new_instance.{{ field.name }} = {{ field.data_type|python.map_data_type }}.load(obj['{{ field.name }}'], parse=False)
                    {% else %}
        new_instance.{{field.name}} = {{ field|python_django.class_name }}.load(obj['{{ field.name }}'], parse=False)
                    {% endif %}
                {% else %}
                    {% if field.data_type is string %}
        new_instance.{{field.name}} = [{{ field.data_type|python.map_data_type }}.load(item, parse=False)
                                       for item in obj['{{ field.name }}']]
                    {% else %}
        new_instance.{{field.name}} = [{{ field|python_django.class_name }}.load(item, parse=False)
                                       for item in obj['{{ field.name }}']]
                    {% endif %}
                {% endif %}
            {% else %}
        new_instance.{{ field.name }} = obj['{{ field.name }}']
            {% endif %}
        {% endfor %}

{% endmacro %}

{% for message in messages %}
{{ make_message(message) }}
{% endfor %}
