from django import template
from rolepermissions.checkers import has_role

register = template.Library()


@register.simple_tag
def user_has_role(user, roles):
    """
    Check if user has any of the specified roles.

    Usage in templates:
        {% user_has_role user "admin,super_admin" as is_admin %}
        {% if is_admin %}...{% endif %}

    Args:
        user: Django user object
        roles: Comma-separated string of role names

    Returns:
        bool: True if user has any of the roles
    """
    if not user or not user.is_authenticated:
        return False

    role_list = [role.strip() for role in roles.split(",")]
    return has_role(user, role_list)


@register.filter
def has_any_role(user, roles):
    """
    Template filter to check if user has any of the specified roles.

    Usage in templates:
        {% if user|has_any_role:"admin,super_admin" %}...{% endif %}

    Args:
        user: Django user object
        roles: Comma-separated string of role names

    Returns:
        bool: True if user has any of the roles
    """
    if not user or not user.is_authenticated:
        return False

    role_list = [role.strip() for role in roles.split(",")]
    return has_role(user, role_list)


@register.filter
def has_specific_role(user, role):
    """
    Template filter to check if user has a specific role.

    Usage in templates:
        {% if user|has_specific_role:"admin" %}...{% endif %}

    Args:
        user: Django user object
        role: Single role name

    Returns:
        bool: True if user has the role
    """
    if not user or not user.is_authenticated:
        return False

    return has_role(user, role)
