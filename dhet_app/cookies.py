from django.conf import settings

# Default cookie configurations
# To customize, add COOKIE_CONSENT_GROUPS to your settings.py
DEFAULT_COOKIE_GROUPS = [
    {
        "varname": "essential",
        "name": "Essential",
        "description": "These cookies are necessary for the website to function and cannot be switched off. They are usually only set in response to actions made by you which amount to a request for services, such as setting your privacy preferences, logging in or filling in forms.",
        "is_required": True,
        "is_deletable": False,
    },
    {
        "varname": "analytics",
        "name": "Analytics",
        "description": "These cookies allow us to count visits and traffic sources so we can measure and improve the performance of our site. They help us to know which pages are the most and least popular and see how visitors move around the site.",
        "is_required": False,
        "is_deletable": True,
    },
    {
        "varname": "preferences",
        "name": "Preferences",
        "description": "These cookies enable the website to provide enhanced functionality and personalisation. They may be set by us or by third party providers whose services we have added to our pages.",
        "is_required": False,
        "is_deletable": True,
    },
]

def get_cookie_config():
    """
    Returns the cookie configuration from settings or defaults.
    """
    return getattr(settings, "COOKIE_CONSENT_GROUPS", DEFAULT_COOKIE_GROUPS)
