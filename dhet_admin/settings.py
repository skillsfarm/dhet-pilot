from typing import Any

from django.conf import settings

from dhet_admin.widgets import (
    BUTTON_CLASSES,
    CHECKBOX_CLASSES,
    FILE_CLASSES,
    INPUT_CLASSES,
    RADIO_CLASSES,
    SWITCH_CLASSES,
)

CONFIG_DEFAULTS = {
    "SITE_TITLE": "DHET",
    "SITE_HEADER": "DHET",
    "SITE_SUBHEADER": "Admin Panel",
    "SITE_DROPDOWN": None,
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": "/staticfiles/images/branding/logo-icon-light.png",
        "dark": "/staticfiles/images/branding/logo-icon-dark.png",
    },
    "SITE_SYMBOL": None,
    "SITE_LOGO": None,
    "SITE_FAVICONS": [],
    "BORDER_RADIUS": "var(--radius)",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_LANGUAGES": False,
    "LANGUAGE_FLAGS": {},
    "SHOW_BACK_BUTTON": False,
    "FORMS": {
        "classes": {
            "text_input": " ".join(INPUT_CLASSES),
            "checkbox": " ".join(CHECKBOX_CLASSES),
            "button": " ".join(BUTTON_CLASSES),
            "radio": " ".join(RADIO_CLASSES),
            "switch": " ".join(SWITCH_CLASSES),
            "file": " ".join(FILE_CLASSES),
        },
    },
    "COLORS": {
        # Neutral gray scale matching theme/main.css
        "base": {
            # Light mode
            "50": "oklch(0.9850 0 0)",  # near white
            "100": "oklch(0.9700 0 0)",  # muted, accent
            "200": "oklch(0.9220 0 0)",  # border, input
            "300": "oklch(0.8520 0 0)",
            "400": "oklch(0.7080 0 0)",  # ring
            "500": "oklch(0.5560 0 0)",  # muted-foreground
            "600": "oklch(0.4390 0 0)",
            # Dark mode layers
            "700": "oklch(0.3710 0 0)",  # dark accent
            "800": "oklch(0.2690 0 0)",  # popover, muted - card/elevated
            "900": "oklch(0.2050 0 0)",  # card, sidebar - mid layer
            "950": "oklch(0.1450 0 0)",  # background - darkest
        },
        # Golden/amber primary color
        "primary": {
            "50": "oklch(97.8% 0.03 85.574)",
            "100": "oklch(95.4% 0.05 85.574)",
            "200": "oklch(90.1% 0.08 85.574)",
            "300": "oklch(85% 0.10 85.574)",
            "400": "oklch(80% 0.12 85.574)",
            "500": "oklch(77.088% 0.13804 85.574)",
            "600": "oklch(70% 0.14 85.574)",
            "700": "oklch(60% 0.12 85.574)",
            "800": "oklch(50% 0.10 85.574)",
            "900": "oklch(40% 0.08 85.574)",
            "950": "oklch(30% 0.06 85.574)",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",
            "subtle-dark": "var(--color-base-400)",
            "default-light": "var(--color-base-600)",
            "default-dark": "var(--color-base-300)",
            "important-light": "var(--color-base-950)",
            "important-dark": "var(--color-base-50)",
        },
    },
    "DASHBOARD_CALLBACK": None,
    "ENVIRONMENT": None,
    "ENVIRONMENT_TITLE_PREFIX": None,
    "STYLES": ["css/main.css"],
    "SCRIPTS": [],
    "ACCOUNT": {
        "navigation": [],
    },
    "LANGUAGES": {
        "action": None,
        "navigation": [],
    },
    "COMMAND": {
        "search_models": False,  # Enable search in the models
        "show_history": False,  # Enable history in the command search
        "search_callback": None,  # Inject a custom callback to the search form
    },
    "SIDEBAR": {
        "show_search": False,
        "command_search": False,
        "show_all_applications": False,
        "navigation": [],
    },
    "TABS": [],
    "LOGIN": {
        "image": None,
        "redirect_after": None,
        "form": None,
    },
    "EXTENSIONS": {"modeltranslation": {"flags": {}}},
}


def get_config(settings_name=None):
    if settings_name is None:
        settings_name = "DHET_ADMIN"

    def merge_dicts(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
        result = dict1.copy()

        for key, value in dict2.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value

        return result

    return merge_dicts(CONFIG_DEFAULTS, getattr(settings, settings_name, {}))
