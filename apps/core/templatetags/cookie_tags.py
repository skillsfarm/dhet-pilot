from django import template
from django.utils.html import json_script
from cookie_consent.models import CookieGroup
from cookie_consent.util import get_cookie_value_from_request

register = template.Library()

@register.simple_tag
def all_cookie_groups_extended(request, element_id: str):
    """
    Returns ALL cookie groups (including required) and includes current acceptance status.
    """
    groups = CookieGroup.objects.all().prefetch_related("cookie_set")
    value = []
    
    for group in groups:
        group_data = group.for_json()
        # Add the current acceptance status
        accepted = get_cookie_value_from_request(request, group.varname)
        group_data["accepted"] = accepted if accepted is not None else group.is_required
        value.append(group_data)
        
    return json_script(value, element_id)
