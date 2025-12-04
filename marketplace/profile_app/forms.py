from django import forms


class ImageUploadForm(forms.Form):
    """Форма загрузки изображения аватара"""

    avatar = forms.ImageField(label="Avatar image")
