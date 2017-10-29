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

{% for model in schema.visit_models() %}
class {{ model.name }}(Base):
    __tablename__ = '{{ model.name }}'

    {% for fieldname, field in model.fields.items() %}
        {% if field.kind in ('required', 'optional') %}
    {{ fieldname }} = Column({{ field|sqlalchemy.datatype }})
        {% else %}
    {{fieldname}} = relationship()
        {% endif %}
    {% endfor %}


{% endfor %}

