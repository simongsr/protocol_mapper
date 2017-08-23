import enum

from sqlalchemy import Column, Integer, Float, String, Table, ForeignKey
from sqlalchemy.orm import relationship

__author__  = 'ProtocolMapper by Simone Pandolfi'
__email__   = 'simopandolfi@gmail.com'
{% if version is defined %}
__version__ = {{ version }}
{% endif %}

""" This file was generated by ProtocolMapper
    Checkout the repo for more informations [https://github.com/simongsr/protocol_mapper]
"""

{%- macro make_model(model) -%}
class {{ model|sqlalchemy.modelname }}(Base):
    __tablename__ = '{{ model|sqlalchemy.modelname }}'

    {% for field in model.fields.values() if field.multiplicity != 'repeated' and field|core.is_raw_type %}
    {{ field.name }} = Column({{ field|sqlalchemy.datatype }})
    {% endfor %}

    {% for field in model.fields.values() if field.multiplicity != 'repeated' and not field|core.is_raw_type %}
    {{ field.name }} = relationship({{ field|sqlalchemy.datatype }}
        {%- if field|sqlalchemy.column_constraints_count > 0 -%}
    , {{ field|sqlalchemy.column_constraints|join(', ') }}
        {%- endif -%}
    )
    {% endfor %}

    {% for field in model.fields.values() if field.id > 0 and field.multiplicity == 'repeated' and not field|core.is_raw_type %}
    {{field.name}} = relationship({{ field|sqlalchemy.datatype }}, secondary={{ field|sqlalchemy.association_tablename }}
        {%- if field|sqlalchemy.column_constraints_count > 0 -%}
    , {{ field|sqlalchemy.column_constraints|join(', ') }}
        {%- endif -%}
    )
    {% endfor %}

    # TODO gestire il caso multiplicity == 'repeated' and field.id > 0 and field|core.is_raw_type
    {% for field in model.fields.values() if field.id > 0 and field.multiplicity == 'repeated' and field|core.is_raw_type %}
    {{ field.name }} = relationship({{ field|sqlalchemy.datatype }})  # TODO da fare
    {% endfor %}

    # TODO gestire i casi dei riferimenti reversi

{% for submodel in model|core.nested_models %}
{{ make_model(submodel) }}
{% else %}



{% endfor %}
{%- endmacro %}



{% for enum in enums %}
class {{ enum.name }}(enum.Enum):
    {% for key, value in enum['items'].items() %}
    {{ key }} = {{ value|core.enum_value }}
    {% endfor %}
{% endfor %}


{% for model in schema|core.models %}
    {% for field in model.fields.values() if field.id > 0 and field.multiplicity == 'repeated' and not field|core.is_raw_type %}
{{field | sqlalchemy.association_tablename}} = Table(
    '{{ field|sqlalchemy.association_tablename }}', Base.metadata,
#    Column('{{ field.parent|sqlalchemy.modelname }}_id', Integer,ForeignKey('{{ field.parent|sqlalchemy.modelname }}.id')),  # TODO ATTENZIONE! Non è detto che il modello abbia una sola chiave primaria e che questa si chiami 'id'
#    Column('{{ field.data_type|sqlalchemy.modelname }}_id', Integer, ForeignKey('{{ field.data_type|sqlalchemy.modelname }}.id'))
        {% for keyfield in field.parent|core.key_fields %}
    Column('{{ keyfield.parent|sqlalchemy.modelname }}___{{ keyfield.name }}', {{ keyfield.data_type }}, ForeignKey('{{ keyfield.parent|sqlalchemy.modelname }}.{{ keyfield.name }}')),
        {% endfor %}
        {% for keyfield in field.data_type|core.key_fields %}
    Column('{{ field.data_type|sqlalchemy.modelname }}___{{ keyfield.name }}', {{keyfield.data_type}}, ForeignKey('{{ field.data_type|sqlalchemy.modelname }}.{{ keyfield.name }}')),
        {% endfor %}
)


    {% endfor %}
{% endfor %}


{% for model in models %}
{{ make_model(model) }}
{% endfor %}

