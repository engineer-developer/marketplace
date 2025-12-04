from django import forms
from django.core.validators import FileExtensionValidator


class CSVImportForm(forms.Form):
    """Форма для выбора CSV файла"""

    csv_file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=["csv"])],
        label="CSV file",
        label_suffix=" ->",
        help_text="Необходимо выбрать файл с расширением *.json",
    )


class JsonImportForm(forms.Form):
    """Форма для выбора JSON файла"""

    json_file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=["json"])],
        label="JSON file",
        label_suffix=" ->",
        help_text="Необходимо выбрать файл с расширением *.json",
    )
