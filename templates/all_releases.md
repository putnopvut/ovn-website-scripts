{%- macro branch_block(branch) %}
### OVN {{ branch }}
For more details, see [{{ branch}} ](../{{ branch }})
{% endmacro -%}

+++
title = "All Releases"
+++

## Supported Releases
{%- for branch in supported_branches %}
{{ branch_block(branch) }}
{% endfor %}
## Unsupported Releases
{%- for branch in unsupported_branches %}
{{ branch_block(branch) }}
{% endfor -%}
