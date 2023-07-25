{% macro linkify_commit(commit) -%}
[{{ commit.hexsha[:8] }}]({{ github_url }}/commit/{{ commit.hexsha }})
{%- endmacro -%}

+++
title = "Changelog {{ end_tag }}"
[_build]
  list = 'never'
+++

### Changes from {{ start_tag }} to {{ end_tag }}
{% for commit in commits %}
- {{ linkify_commit(commit) }} {{ commit.summary }}
{%- endfor %}
