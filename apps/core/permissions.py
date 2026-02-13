from rolepermissions.checkers import has_role


def is_content_manager_or_admin(user):
    return (
        user.is_superuser
        or user.is_staff
        or has_role(user, ["content_manager", "admin", "super_admin"])
    )


def is_admin_or_super_admin(user):
    return (
        user.is_superuser or user.is_staff or has_role(user, ["admin", "super_admin"])
    )


def is_super_admin(user):
    return user.is_superuser or has_role(user, "super_admin")


def has_any_role(user, roles):
    if user.is_superuser or user.is_staff:
        return True
    return has_role(user, roles)
