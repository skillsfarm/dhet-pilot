from dhet_admin.contrib.filters.admin.dropdown_filters import (
    MultipleRelatedDropdownFilter,
    RelatedDropdownFilter,
)
from dhet_admin.contrib.filters.admin.mixins import AutocompleteMixin
from dhet_admin.contrib.filters.forms import AutocompleteDropdownForm


class AutocompleteSelectFilter(AutocompleteMixin, RelatedDropdownFilter):
    form_class = AutocompleteDropdownForm


class AutocompleteSelectMultipleFilter(
    AutocompleteMixin, MultipleRelatedDropdownFilter
):
    form_class = AutocompleteDropdownForm
