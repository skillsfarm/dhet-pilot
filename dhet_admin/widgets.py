import json
import warnings
from collections.abc import Callable
from typing import Any

from django.conf import settings
from django.contrib.admin.options import VERTICAL
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.widgets import (
    AdminBigIntegerFieldWidget,
    AdminDateWidget,
    AdminEmailInputWidget,
    AdminFileWidget,
    AdminIntegerFieldWidget,
    AdminRadioSelect,
    AdminSplitDateTime,
    AdminTextareaWidget,
    AdminTextInputWidget,
    AdminTimeWidget,
    AdminURLFieldWidget,
    AdminUUIDInputWidget,
    ForeignKeyRawIdWidget,
    RelatedFieldWidgetWrapper,
)
from django.db.models import ManyToOneRel
from django.forms import (
    CheckboxInput,
    CheckboxSelectMultiple,
    ClearableFileInput,
    MultiWidget,
    NullBooleanSelect,
    NumberInput,
    PasswordInput,
    Select,
    SelectMultiple,
)
from django.forms.widgets import Input
from django.utils.translation import gettext_lazy as _

from dhet_admin.exceptions import DhetAdminException

BUTTON_CLASSES = [
    "border",
    "cursor-pointer",
    "font-medium",
    "px-3",
    "py-2",
    "rounded-default",
    "text-center",
    "whitespace-nowrap",
    "bg-primary-600",
    "border-transparent",
    "text-white",
]

LABEL_CLASSES = [
    "block",
    "font-semibold",
    "mb-2",
    "text-font-important-light",
    "text-sm",
    "dark:text-font-important-dark",
]

CHECKBOX_LABEL_CLASSES = [
    "font-semibold",
    "ml-2",
    "text-sm",
    "text-font-important-light",
    "dark:text-font-important-dark",
]

BASE_CLASSES = [
    "border",
    "border-base-200",
    "bg-white",
    "font-medium",
    "min-w-20",
    "placeholder-base-400",
    "rounded-default",
    "shadow-xs",
    "text-font-default-light",
    "text-sm",
    "focus:outline-2",
    "focus:-outline-offset-2",
    "focus:outline-primary-600",
    "group-[.errors]:border-red-600",
    "focus:group-[.errors]:outline-red-600",
    "dark:bg-base-900",
    "dark:border-base-700",
    "dark:text-font-default-dark",
    "dark:group-[.errors]:border-red-500",
    "dark:focus:group-[.errors]:outline-red-500",
    "dark:scheme-dark",
    "group-[.primary]:border-transparent",
    "disabled:!bg-base-50",
    "dark:disabled:!bg-base-800",
]

BASE_INPUT_CLASSES = [
    *BASE_CLASSES,
    "px-3",
    "py-2",
    "w-full",
]

INPUT_CLASSES = [*BASE_INPUT_CLASSES, "max-w-2xl"]

DATETIME_CLASSES = [*BASE_INPUT_CLASSES, "min-w-52"]

COLOR_CLASSES = [*BASE_CLASSES, "h-[38px]", "px-2", "py-2", "w-32"]

INPUT_CLASSES_READONLY = [*BASE_INPUT_CLASSES, "bg-base-50"]

TEXTAREA_CLASSES = [
    *BASE_INPUT_CLASSES,
    "max-w-4xl",
    "appearance-none",
    "expandable",
    "transition",
    "transition-height",
    "duration-75",
    "ease-in-out",
]

TEXTAREA_EXPANDABLE_CLASSES = [
    "block",
    "field-sizing-content",
    "min-h-[38px]",
]

SELECT_CLASSES = [
    *BASE_INPUT_CLASSES,
    "pr-8!",
    "max-w-2xl",
    "appearance-none",
    "text-ellipsis",
]

PROSE_CLASSES = [
    "font-normal",
    "whitespace-normal",
    "prose-sm",
    "prose-blockquote:border-l-4",
    "prose-blockquote:not-italic",
    "prose-pre:bg-base-50",
    "prose-pre:rounded-default",
    "prose-headings:font-medium",
    "prose-a:text-primary-600",
    "prose-headings:font-medium",
    "prose-headings:text-base-700",
    "prose-ol:list-decimal",
    "prose-ul:list-disc",
    "prose-strong:text-base-700",
    "dark:prose-pre:bg-base-800",
    "dark:prose-blockquote:border-base-700",
    "dark:prose-blockquote:text-base-300",
    "dark:prose-headings:text-base-200",
    "dark:prose-strong:text-base-200",
]

CHECKBOX_CLASSES = [
    "appearance-none",
    "bg-white",
    "block",
    "border",
    "border-base-300",
    "cursor-pointer",
    "h-4",
    "min-w-4",
    "relative",
    "rounded-[4px]",
    "shadow-xs",
    "w-4",
    "hover:border-base-400",
    "dark:bg-base-700",
    "dark:border-base-500",
    "dark:checked:after:text-white",
    "focus:outline",
    "focus:outline-2",
    "focus:outline-offset-2",
    "focus:outline-primary-500",
    "after:absolute",
    r"after:content-['check\_small']",
    "after:flex!",
    "after:h-4",
    "after:items-center",
    "after:justify-center",
    "after:leading-none",
    "after:material-symbols-outlined",
    "after:-ml-px",
    "after:-mt-px",
    "after:text-white",
    "after:transition-all",
    "after:w-4",
    "dark:after:text-base-700",
    "checked:bg-primary-600",
    "dark:checked:bg-primary-600",
    "checked:border-primary-600",
    "dark:checked:border-primary-600",
    "checked:transition-all",
    "checked:hover:border-primary-600",
]

RADIO_CLASSES = [
    "appearance-none",
    "bg-white",
    "block",
    "border",
    "border-base-300",
    "cursor-pointer",
    "h-4",
    "min-w-4",
    "relative",
    "rounded-full",
    "w-4",
    "dark:bg-base-700",
    "dark:border-base-500",
    "hover:border-base-400",
    "focus:outline",
    "focus:outline-2",
    "focus:outline-offset-2",
    "focus:outline-primary-500",
    "after:absolute",
    "after:bg-transparent",
    "after:content-['']",
    "after:flex",
    "after:h-2",
    "after:items-center",
    "after:justify-center",
    "after:leading-none",
    "after:left-1/2",
    "after:rounded-full",
    "after:text-white",
    "after:top-1/2",
    "after:transition-all",
    "after:-translate-x-1/2",
    "after:-translate-y-1/2",
    "after:text-sm",
    "after:w-2",
    "dark:after:text-base-700",
    "dark:after:bg-transparent",
    "checked:bg-primary-600",
    "checked:border-primary-600",
    "checked:transition-all",
    "checked:after:bg-white",
    "dark:checked:after:bg-base-900",
    "checked:hover:border-base-900/20",
]

SWITCH_CLASSES = [
    "appearance-none",
    "bg-base-300",
    "block",
    "cursor-pointer",
    "h-5",
    "relative",
    "rounded-full",
    "transition-colors",
    "w-8",
    "min-w-8",
    "disabled:cursor-not-allowed",
    "disabled:opacity-50",
    "focus:outline-none",
    "after:absolute",
    "after:bg-white",
    "after:content-['']",
    "after:bg-red-300",
    "after:h-3",
    "after:rounded-full",
    "after:shadow-xs",
    "after:transition-all",
    "after:left-1",
    "after:top-1",
    "after:w-3",
    "checked:bg-green-500",
    "checked:after:left-4",
    "dark:bg-base-600",
    "dark:checked:bg-green-700",
]

FILE_CLASSES = [
    "bg-white",
    "border",
    "border-base-200",
    "flex",
    "grow",
    "items-center",
    "overflow-hidden",
    "rounded-default",
    "shadow-xs",
    "max-w-2xl",
    "focus-within:outline-2",
    "focus-within:-outline-offset-2",
    "focus-within:outline-primary-600",
    "group-[.errors]:border-red-600",
    "focus-within:group-[.errors]:outline-red-500",
    "dark:bg-base-900",
    "dark:border-base-700",
    "dark:group-[.errors]:border-red-500",
    "dark:focus-within:group-[.errors]:outline-red-500",
]


class DhetAdminPrefixSuffixMixin(Input):
    def get_context(
        self, name: str, value: Any, attrs: dict[str, Any] | None
    ) -> dict[str, Any]:
        context = super().get_context(name, value, attrs)
        widget = context["widget"]

        if "prefix" in self.attrs:
            widget["prefix"] = self.attrs["prefix"]
            del self.attrs["prefix"]

        if "prefix_icon" in self.attrs:
            widget["prefix_icon"] = self.attrs["prefix_icon"]
            self.attrs["class"] = " ".join([self.attrs["class"], "pl-9"])
            del self.attrs["prefix_icon"]

        if "suffix" in self.attrs:
            widget["suffix"] = self.attrs["suffix"]
            del self.attrs["suffix"]

        if "suffix_icon" in self.attrs:
            widget["suffix_icon"] = self.attrs["suffix_icon"]
            self.attrs["class"] = " ".join([self.attrs["class"], "pr-9"])
            del self.attrs["suffix_icon"]

        widget.update(
            {
                "name": name,
                "is_hidden": self.is_hidden,
                "required": self.is_required,
                "value": self.format_value(value),
                "attrs": self.build_attrs(self.attrs, attrs),
                "template_name": self.template_name,
            }
        )

        return {
            "widget": widget,
        }


class DhetAdminAdminTextInputWidget(DhetAdminPrefixSuffixMixin, AdminTextInputWidget):
    template_name = "dhet_admin/widgets/text.html"

    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class DhetAdminAdminURLInputWidget(AdminURLFieldWidget):
    template_name = "dhet_admin/widgets/url.html"

    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class DhetAdminAdminColorInputWidget(AdminTextInputWidget):
    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "type": "color",
                "class": " ".join(
                    [*COLOR_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class DhetAdminAdminUUIDInputWidget(AdminUUIDInputWidget):
    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class DhetAdminAdminIntegerRangeWidget(MultiWidget):
    template_name = "dhet_admin/widgets/range.html"

    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        attrs = attrs or {}

        attrs["class"] = " ".join(
            [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
        )

        _widgets = (NumberInput(attrs=attrs), NumberInput(attrs=attrs))

        super().__init__(_widgets, attrs)

    def decompress(self, value: str | None) -> tuple[Callable | None, ...]:
        return (value.lower, value.upper) if value else (None, None)


class DhetAdminAdminEmailInputWidget(AdminEmailInputWidget):
    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class FileFieldMixin(ClearableFileInput):
    def get_context(
        self, name: str, value: Any, attrs: dict[str, Any] | None
    ) -> dict[str, Any]:
        widget = super().get_context(name, value, attrs)

        widget["widget"].update(
            {
                "class": " ".join([*CHECKBOX_CLASSES, *["form-check-input"]]),
                "file_wrapper_class": " ".join(FILE_CLASSES),
                "file_input_class": " ".join(
                    [
                        self.attrs.get("class", ""),
                        *[
                            "opacity-0",
                            "pointer-events-none",
                        ],
                    ]
                ),
            }
        )

        return widget


class DhetAdminAdminImageFieldWidget(FileFieldMixin, AdminFileWidget):
    template_name = "dhet_admin/widgets/clearable_file_input.html"


class DhetAdminAdminFileFieldWidget(FileFieldMixin, AdminFileWidget):
    template_name = "dhet_admin/widgets/clearable_file_input_small.html"


class DhetAdminAdminImageSmallFieldWidget(FileFieldMixin, AdminFileWidget):
    template_name = "dhet_admin/widgets/clearable_file_input_small.html"


class DhetAdminAdminDateWidget(AdminDateWidget):
    template_name = "dhet_admin/widgets/date.html"

    def __init__(
        self, attrs: dict[str, Any] | None = None, format: str | None = None
    ) -> None:
        attrs = {
            **(attrs or {}),
            "class": " ".join(
                [
                    "vDateField",
                    *DATETIME_CLASSES,
                    attrs.get("class", "") if attrs else "",
                ]
            ),
            "size": "10",
        }
        super().__init__(attrs=attrs, format=format)

    class Media:
        js = [
            "admin/js/core.js",
            "admin/js/calendar.js",
            "admin/js/admin/DateTimeShortcuts.js",
        ]


class DhetAdminAdminSingleDateWidget(AdminDateWidget):
    template_name = "dhet_admin/widgets/date.html"

    def __init__(
        self, attrs: dict[str, Any] | None = None, format: str | None = None
    ) -> None:
        attrs = {
            **(attrs or {}),
            "class": " ".join(
                [
                    "vDateField",
                    *DATETIME_CLASSES,
                    attrs.get("class", "") if attrs else "",
                ]
            ),
            "size": "10",
        }
        super().__init__(attrs=attrs, format=format)


class DhetAdminAdminTimeWidget(AdminTimeWidget):
    template_name = "dhet_admin/widgets/time.html"

    def __init__(
        self, attrs: dict[str, Any] | None = None, format: str | None = None
    ) -> None:
        attrs = {
            **(attrs or {}),
            "class": " ".join(
                [
                    "vTimeField",
                    *DATETIME_CLASSES,
                    attrs.get("class", "") if attrs else "",
                ]
            ),
            "size": "8",
        }
        super().__init__(attrs=attrs, format=format)

    class Media:
        js = [
            "admin/js/core.js",
            "admin/js/calendar.js",
            "admin/js/admin/DateTimeShortcuts.js",
        ]


class DhetAdminAdminSingleTimeWidget(AdminTimeWidget):
    template_name = "dhet_admin/widgets/time.html"

    def __init__(
        self, attrs: dict[str, Any] | None = None, format: str | None = None
    ) -> None:
        attrs = {
            **(attrs or {}),
            "class": " ".join(
                [
                    "vTimeField",
                    *DATETIME_CLASSES,
                    attrs.get("class", "") if attrs else "",
                ]
            ),
            "size": "8",
        }
        super().__init__(attrs=attrs, format=format)


class DhetAdminAdminTextareaWidget(AdminTextareaWidget):
    template_name = "dhet_admin/widgets/textarea.html"

    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        attrs = attrs or {}

        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [
                        "vLargeTextField",
                        *TEXTAREA_CLASSES,
                        attrs.get("class", "") if attrs else "",
                    ]
                ),
            }
        )


class DhetAdminAdminExpandableTextareaWidget(DhetAdminAdminTextareaWidget):
    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        attrs = attrs or {}

        attrs.update({"rows": 2})

        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [
                        "vLargeTextField",
                        *TEXTAREA_CLASSES,
                        *TEXTAREA_EXPANDABLE_CLASSES,
                        attrs.get("class", "") if attrs else "",
                    ]
                ),
            }
        )


class DhetAdminAdminSplitDateTimeWidget(AdminSplitDateTime):
    template_name = "dhet_admin/widgets/split_datetime.html"

    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        widgets = [
            DhetAdminAdminDateWidget(attrs={"placeholder": _("Date")}),
            DhetAdminAdminTimeWidget(attrs={"placeholder": _("Time")}),
        ]
        MultiWidget.__init__(self, widgets, attrs)

    class Media:
        js = [
            "admin/js/core.js",
            "admin/js/calendar.js",
            "admin/js/admin/DateTimeShortcuts.js",
        ]


class DhetAdminAdminSplitDateTimeVerticalWidget(AdminSplitDateTime):
    template_name = "dhet_admin/widgets/split_datetime_vertical.html"

    def __init__(
        self,
        attrs: dict[str, Any] | None = None,
        date_attrs: dict[str, Any] | None = None,
        time_attrs: dict[str, Any] | None = None,
        date_label: str | None = None,
        time_label: str | None = None,
    ) -> None:
        self.date_label = date_label
        self.time_label = time_label

        widgets = [
            DhetAdminAdminDateWidget(attrs=date_attrs),
            DhetAdminAdminTimeWidget(attrs=time_attrs),
        ]
        MultiWidget.__init__(self, widgets, attrs)

    def get_context(
        self, name: str, value: Any, attrs: dict[str, Any] | None
    ) -> dict[str, Any]:
        context = super().get_context(name, value, attrs)

        if self.date_label is not None:
            context["date_label"] = self.date_label
        else:
            context["date_label"] = _("Date")

        if self.time_label is not None:
            context["time_label"] = self.time_label
        else:
            context["time_label"] = _("Time")

        return context


class DhetAdminAdminIntegerFieldWidget(AdminIntegerFieldWidget):
    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class DhetAdminAdminDecimalFieldWidget(AdminIntegerFieldWidget):
    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class DhetAdminAdminBigIntegerFieldWidget(AdminBigIntegerFieldWidget):
    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            }
        )


class DhetAdminAdminNullBooleanSelectWidget(NullBooleanSelect):
    template_name = "dhet_admin/widgets/select.html"

    def __init__(self, attrs: dict[str, Any] | None = None) -> None:
        attrs = attrs or {}

        attrs["class"] = " ".join(
            [*SELECT_CLASSES, attrs.get("class", "") if attrs else ""]
        )
        super().__init__(attrs)


class DhetAdminAdminSelectWidget(Select):
    template_name = "dhet_admin/widgets/select.html"

    def __init__(
        self, attrs: dict[str, Any] | None = None, choices: tuple | list = ()
    ) -> None:
        attrs = attrs or {}

        attrs["class"] = " ".join(
            [*SELECT_CLASSES, attrs.get("class", "") if attrs else ""]
        )
        super().__init__(attrs, choices)


class DhetAdminAdminSelect2Widget(Select):
    def __init__(
        self, attrs: dict[str, Any] | None = None, choices: tuple | list = ()
    ) -> None:
        attrs = attrs or {}

        attrs["data-theme"] = "admin-autocomplete"
        attrs["class"] = " ".join(
            ["dhet_admin-admin-autocomplete", attrs.get("class", "") if attrs else ""]
        )

        super().__init__(attrs, choices)

    class Media:
        extra = "" if settings.DEBUG else ".min"
        js = (
            f"admin/js/vendor/jquery/jquery{extra}.js",
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/jquery.init.js",
            "dhet_admin/js/select2.init.js",
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.css",
                "admin/css/autocomplete.css",
            ),
        }


class DhetAdminAdminSelectMultipleWidget(SelectMultiple):
    def __init__(
        self, attrs: dict[str, Any] | None = None, choices: tuple | list = ()
    ) -> None:
        attrs = attrs or {}

        attrs["class"] = " ".join(
            [*SELECT_CLASSES, attrs.get("class", "") if attrs else ""]
        )
        super().__init__(attrs, choices)


class DhetAdminAdminSelect2MultipleWidget(SelectMultiple):
    def __init__(
        self, attrs: dict[str, Any] | None = None, choices: tuple | list = ()
    ) -> None:
        attrs = attrs or {}

        attrs["data-theme"] = "admin-autocomplete"
        attrs["class"] = " ".join(
            [
                "dhet_admin-admin-autocomplete admin-autocomplete",
                attrs.get("class", "") if attrs else "",
            ]
        )

        super().__init__(attrs, choices)

    class Media:
        extra = "" if settings.DEBUG else ".min"
        js = (
            f"admin/js/vendor/jquery/jquery{extra}.js",
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/jquery.init.js",
            "dhet_admin/js/select2.init.js",
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.css",
                "admin/css/autocomplete.css",
            ),
        }


class DhetAdminAdminRadioSelectWidget(AdminRadioSelect):
    template_name = "dhet_admin/widgets/radio.html"
    option_template_name = "dhet_admin/widgets/radio_option.html"

    def __init__(
        self, radio_style: int | None = None, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

        if radio_style is None:
            radio_style = VERTICAL

        self.radio_style = radio_style
        self.attrs["class"] = " ".join([*RADIO_CLASSES, self.attrs.get("class", "")])

    def get_context(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context(*args, **kwargs)
        context.update({"radio_style": self.radio_style})
        return context


class DhetAdminAdminCheckboxSelectMultiple(CheckboxSelectMultiple):
    template_name = "dhet_admin/widgets/radio.html"
    option_template_name = "dhet_admin/widgets/radio_option.html"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.attrs = {
            "class": " ".join(
                [*CHECKBOX_CLASSES, self.attrs.get("class", "") if self.attrs else ""]
            )
        }


class DhetAdminBooleanWidget(CheckboxInput):
    def __init__(
        self, attrs: dict[str, Any] | None = None, check_test: Callable | None = None
    ) -> None:
        attrs = attrs or {}

        super().__init__(
            {
                **(attrs or {}),
                "class": " ".join(
                    [*CHECKBOX_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            },
            check_test,
        )


class DhetAdminBooleanSwitchWidget(CheckboxInput):
    def __init__(
        self, attrs: dict[str, Any] | None = None, check_test: Callable | None = None
    ) -> None:
        super().__init__(
            attrs={
                **(attrs or {}),
                "class": " ".join(
                    [*SWITCH_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            },
            check_test=None,
        )


class DhetAdminRelatedFieldWidgetWrapper(RelatedFieldWidgetWrapper):
    template_name = "dhet_admin/widgets/related_widget_wrapper.html"


class DhetAdminForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    template_name = "dhet_admin/widgets/foreign_key_raw_id.html"

    def __init__(
        self,
        rel: ManyToOneRel,
        admin_site: AdminSite,
        attrs: dict[str, Any] | None = None,
        using: Any | None = None,
    ) -> None:
        attrs = {
            **(attrs or {}),
            "class": " ".join(
                [
                    "vForeignKeyRawIdAdminField",
                    *INPUT_CLASSES,
                    attrs.get("class", "") if attrs else "",
                ]
            ),
        }
        super().__init__(rel, admin_site, attrs, using)


class DhetAdminAdminPasswordWidget(PasswordInput):
    def __init__(
        self, attrs: dict[str, Any] | None = None, render_value: bool = False
    ) -> None:
        super().__init__(
            {
                **(attrs or {}),
                "class": " ".join(
                    [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                ),
            },
            render_value,
        )


class DhetAdminAdminPasswordToggleWidget(DhetAdminAdminPasswordWidget):
    template_name = "dhet_admin/widgets/password_toggle.html"


class DhetAdminAdminPasswordInput(DhetAdminAdminPasswordWidget):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "DhetAdminAdminPasswordInput is deprecated and will be removed in a future release. "
            "Please use DhetAdminAdminPasswordWidget instead.",
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class AutocompleteWidgetMixin:
    is_required: bool

    def __init__(
        self, attrs: dict[str, Any] | None = None, choices: tuple | list = ()
    ) -> None:
        attrs = attrs or {}

        attrs.update(
            {
                "data-ajax--cache": "true",
                "data-ajax--delay": 250,
                "data-ajax--type": "GET",
                "data-theme": "admin-autocomplete",
                "data-allow-clear": json.dumps(not self.is_required),
                "data-placeholder": "",
                "class": " ".join(
                    [
                        "dhet_admin-admin-autocomplete admin-autocomplete",
                        attrs.get("class", "") if attrs else "",
                    ]
                ),
            }
        )
        super().__init__(attrs, choices)


class DhetAdminAdminAutocompleteWidget(AutocompleteWidgetMixin, Select):
    option_template_name = "dhet_admin/widgets/select_option_autocomplete.html"


class DhetAdminAdminAutocompleteModelChoiceFieldWidget(
    AutocompleteWidgetMixin, Select
):
    option_template_name = (
        "dhet_admin/widgets/select_option_modelchoicefield_autocomplete.html"
    )


class DhetAdminAdminMultipleAutocompleteWidget(
    AutocompleteWidgetMixin, SelectMultiple
):
    option_template_name = "dhet_admin/widgets/select_option_autocomplete.html"


class DhetAdminAdminMultipleAutocompleteModelChoiceFieldWidget(
    AutocompleteWidgetMixin, SelectMultiple
):
    option_template_name = (
        "dhet_admin/widgets/select_option_modelchoicefield_autocomplete.html"
    )


try:
    from djmoney.forms.widgets import MoneyWidget
    from djmoney.settings import CURRENCY_CHOICES

    class DhetAdminAdminMoneyWidget(MoneyWidget):
        template_name = "dhet_admin/widgets/split_money.html"

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            attrs = {}

            if "attrs" in kwargs:
                attrs = kwargs.pop("attrs")

            super().__init__(
                amount_widget=DhetAdminAdminTextInputWidget(attrs=attrs),
                currency_widget=DhetAdminAdminSelectWidget(
                    choices=CURRENCY_CHOICES,
                    attrs={
                        "aria-label": _("Select currency"),
                    },
                ),
            )

except ImportError:

    class DhetAdminAdminMoneyWidget:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise DhetAdminException("django-money not installed")


try:
    from location_field.widgets import LocationWidget

    class DhetAdminAdminLocationWidget(LocationWidget):
        def __init__(self, attrs: dict[str, Any] | None = None, **kwargs: Any) -> None:
            based_fields = kwargs.pop("based_fields", [])
            super().__init__(
                attrs={
                    **(attrs or {}),
                    "class": " ".join(
                        [*INPUT_CLASSES, attrs.get("class", "") if attrs else ""]
                    ),
                },
                based_fields=based_fields,
                **kwargs,
            )
except ImportError:

    class DhetAdminAdminLocationWidget:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise DhetAdminException("django-location-field not installed")
