DHET_ADMIN_CONSTANCE_ADDITIONAL_FIELDS = {
    str: [
        "django.forms.CharField",
        {
            "widget": "dhet_admin.widgets.DhetAdminAdminTextInputWidget",
            "required": False,
        },
    ],
    int: [
        "django.forms.IntegerField",
        {
            "widget": "dhet_admin.widgets.DhetAdminAdminIntegerFieldWidget",
        },
    ],
    float: [
        "django.forms.FloatField",
        {
            "widget": "dhet_admin.widgets.DhetAdminAdminDecimalFieldWidget",
        },
    ],
    bool: [
        "django.forms.BooleanField",
        {
            "widget": "dhet_admin.widgets.DhetAdminBooleanSwitchWidget",
            "required": False,
        },
    ],
    "file_field": [
        "django.forms.fields.FileField",
        {
            "widget": "dhet_admin.widgets.DhetAdminAdminFileFieldWidget",
        },
    ],
    "image_field": [
        "django.forms.fields.ImageField",
        {
            "widget": "dhet_admin.widgets.DhetAdminAdminImageFieldWidget",
        },
    ],
}
