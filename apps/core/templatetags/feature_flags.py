from django import template

from apps.core.models import FeatureFlag

register = template.Library()


@register.simple_tag
def feature_enabled(key):
    return FeatureFlag.is_enabled_key(key)
