{{ objname | escape | underline}}

.. currentmodule:: {{ module }}

.. autoclass:: {{ objname }}

    {% block attributes_summary %}
    {% if attributes %}

    .. rubric:: Attributes Summary

    .. autosummary::
    {% for item in attributes %}
        {%- if item not in inherited_members %}
            ~{{ item }}
        {%- endif %}
    {%- endfor %}

    {% endif %}
    {% endblock %}

    {% block methods_summary %}
    {% if methods %}

    {% if '__init__' in methods %}
        {% set caught_result = methods.remove('__init__') %}
    {% endif %}

    .. rubric:: Methods Summary

    .. autosummary::
        :toctree: {{ objname }}/methods
        :nosignatures:

    {% for item in methods %}
        {%- if item not in inherited_members %}
            ~{{ name }}.{{ item }}
        {%- endif %}
    {%- endfor %}

    {% endif %}
    {% endblock %}

    {% block methods_documentation %}
    {% if methods %}

    .. rubric:: Methods Documentation

    {% for item in methods %}
        {%- if item not in inherited_members %}
    .. automethod:: {{ name }}.{{ item }}
        {%- endif %}
    {%- endfor %}

    {% endif %}
    {% endblock %}
