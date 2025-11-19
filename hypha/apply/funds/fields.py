from django import forms
from django.utils import formats


def sanitize_separators(value):
    if not isinstance(value, str):
        return value

    # Remove any whitespace
    value = value.replace(" ", "")

    # Normalize the decimal separator:
    decimal_separator = formats.get_format("DECIMAL_SEPARATOR", use_l10n=True)
    if decimal_separator in value:
        integer_part, decimal_part = value.split(decimal_separator, 1)
    else:
        integer_part, decimal_part = value, None

    # Remove any thousand separator
    thousand_separator = formats.get_format("THOUSAND_SEPARATOR", use_l10n=True)
    integer_part = integer_part.replace(thousand_separator, "")

    if decimal_part is None:
        return integer_part
    else:
        return f"{integer_part}.{decimal_part}"


class LocalizedCurrencyField(forms.FloatField):
    def to_python(self, value):
        value = sanitize_separators(value)
        return super().to_python(value)
