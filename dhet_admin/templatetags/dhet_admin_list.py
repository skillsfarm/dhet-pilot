"""
Template tags for DHET Admin list views.
This module provides template tags for pagination and list functionality.
"""

from django import template

# Import paginator_number from dhet_admin_result_list where it's already defined
from dhet_admin.templatetags.dhet_admin_result_list import paginator_number

register = template.Library()

# Register the paginator_number tag from dhet_admin_result_list
register.simple_tag(paginator_number)


@register.inclusion_tag("admin/pagination.html", takes_context=True)
def pagination(context):
    """
    Generate the pagination controls for admin list views.
    """
    return context
