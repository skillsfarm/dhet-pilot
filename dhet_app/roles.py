from rolepermissions.roles import AbstractUserRole


class User(AbstractUserRole):
    verbose_name = "User"
    available_permissions = {"edit_own_profile": True}


class Developer(AbstractUserRole):
    verbose_name = "Developer"
    available_permissions = {
        "edit_own_profile": True,
        "access_api_docs": True,
    }


class ContentManager(AbstractUserRole):
    verbose_name = "Content Manager"
    available_permissions = {
        "edit_own_profile": True,
        "manage_content": True,
    }


class Admin(AbstractUserRole):
    verbose_name = "Admin"
    available_permissions = {
        "edit_own_profile": True,
        "manage_users": True,
    }


class SuperAdmin(AbstractUserRole):
    verbose_name = "Super Admin"
    available_permissions = {
        "edit_own_profile": True,
        "manage_users": True,
        "edit_system_settings": True,
    }
