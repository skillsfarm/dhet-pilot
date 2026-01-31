import copy

from django import forms
from django.db import models

from dhet_admin import widgets

FORMFIELD_OVERRIDES = {
    models.DateTimeField: {
        "form_class": forms.SplitDateTimeField,
        "widget": widgets.DhetAdminAdminSplitDateTimeWidget,
    },
    models.DateField: {"widget": widgets.DhetAdminAdminSingleDateWidget},
    models.TimeField: {"widget": widgets.DhetAdminAdminSingleTimeWidget},
    models.EmailField: {"widget": widgets.DhetAdminAdminEmailInputWidget},
    models.CharField: {"widget": widgets.DhetAdminAdminTextInputWidget},
    models.URLField: {"widget": widgets.DhetAdminAdminURLInputWidget},
    models.GenericIPAddressField: {"widget": widgets.DhetAdminAdminTextInputWidget},
    models.UUIDField: {"widget": widgets.DhetAdminAdminUUIDInputWidget},
    models.TextField: {"widget": widgets.DhetAdminAdminTextareaWidget},
    models.NullBooleanField: {"widget": widgets.DhetAdminAdminNullBooleanSelectWidget},
    models.BooleanField: {"widget": widgets.DhetAdminBooleanSwitchWidget},
    models.IntegerField: {"widget": widgets.DhetAdminAdminIntegerFieldWidget},
    models.BigIntegerField: {"widget": widgets.DhetAdminAdminBigIntegerFieldWidget},
    models.DecimalField: {"widget": widgets.DhetAdminAdminDecimalFieldWidget},
    models.FloatField: {"widget": widgets.DhetAdminAdminDecimalFieldWidget},
    models.FileField: {"widget": widgets.DhetAdminAdminFileFieldWidget},
    models.ImageField: {"widget": widgets.DhetAdminAdminImageFieldWidget},
    models.JSONField: {"widget": widgets.DhetAdminAdminTextareaWidget},
    models.DurationField: {"widget": widgets.DhetAdminAdminTextInputWidget},
}

######################################################################
# Postgres
######################################################################
try:
    from django.contrib.postgres.fields import ArrayField, IntegerRangeField
    from django.contrib.postgres.search import SearchVectorField

    FORMFIELD_OVERRIDES.update(
        {
            ArrayField: {"widget": widgets.DhetAdminAdminTextareaWidget},
            SearchVectorField: {"widget": widgets.DhetAdminAdminTextareaWidget},
            IntegerRangeField: {"widget": widgets.DhetAdminAdminIntegerRangeWidget},
        }
    )
except ImportError:
    pass

######################################################################
# Django Money
######################################################################
try:
    from djmoney.models.fields import MoneyField

    FORMFIELD_OVERRIDES.update(
        {
            MoneyField: {"widget": widgets.DhetAdminAdminMoneyWidget},
        }
    )
except ImportError:
    pass

######################################################################
# Inlines
######################################################################
FORMFIELD_OVERRIDES_INLINE = copy.deepcopy(FORMFIELD_OVERRIDES)

FORMFIELD_OVERRIDES_INLINE.update(
    {
        models.ImageField: {"widget": widgets.DhetAdminAdminImageSmallFieldWidget},
    }
)
