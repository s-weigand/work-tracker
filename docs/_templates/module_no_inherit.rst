{% block module %}
{{ fullname | replace("work_tracker.", "") | escape | underline}}
{#{% set reduced_name={child_modules} %}#}

.. currentmodule:: {{ module }}

.. automodule:: {{ fullname }}

    {% if fullname in known_packages %}
    .. rubric:: Submodules

    .. autosummary::
        {% for item in child_modules %}
            {% if item.startswith( fullname + ".") %}
                {{ item }}
            {% endif %}
        {%- endfor %}
    {% endif %}


    {% block functions %}
    {% if functions %}

    .. rubric:: Summary

    .. autosummary::
        :toctree: {{ fullname | replace("work_tracker.", "") | replace(".", "/") }}/functions
        :nosignatures:
        {% for item in functions %}
        {{ item }}
        {%- endfor %}
    {% endif %}
    {% endblock %}


    {% block classes %}
    {% if classes %}

    .. rubric:: Summary

    .. autosummary::
        :toctree: {{ fullname | replace("work_tracker.", "") | replace(".", "/") }}/classes
        :nosignatures:
        :template: class_no_inherit.rst
    {% for item in classes %}
        {{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}


    {% block exceptions %}
    {% if exceptions %}

    .. rubric:: Exception Summary

    .. autosummary::
        :toctree: {{ fullname | replace("work_tracker.", "") | replace(".", "/") }}/exceptions
        :nosignatures:
    {% for item in exceptions %}
        {{ item }}
    {%- endfor %}
    {% endif %}
    {% endblock %}


{% endblock %}
