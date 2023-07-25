{% macro date_string(date) -%}
{{ date.strftime("%-d %B, %Y") }}
{%- endmacro -%}
+++
title = "{{ branch }}"
{%- if today >= end_date %}
[_build]
  list = 'never'
{% else %}
weight = {{ weight }}
{%- endif %}
+++

## OVN {{ branch }} 

OVN {{ branch }} was initially released on {{ date_string(release_date) }}. 
{% if today < crit_date -%}
This version of OVN is currently supported for all bug fixes. 
{% if is_lts -%}
This version will enter critical fix mode on {{ date_string(crit_date) }}. 
{% endif -%}
Support for this version will end on {{ date_string(end_date) }}. 
{% elif today < end_date -%}
This version of OVN is currently supported for critical and security fixes only. 
Support will end on {{ date_string(end_date) }}. 
{% else -%}
This version of OVN is no longer supported. Support ended on {{ date_string(end_date) }}.
{% endif -%}

{% for release in releases %}
### {{ release.tag }}
{{ release.tag }} was released on {{ date_string(release.release_date) }}.

[Github link]({{ release.url }})

Release Notes:
```
{{ release.news }}
```
[Changelog]({{ release.changelog_path }})
{% endfor %}
