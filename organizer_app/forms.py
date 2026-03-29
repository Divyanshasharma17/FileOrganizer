from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class MultipleFileInput(forms.ClearableFileInput):
    """Widget that allows selecting multiple files."""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Field that accepts multiple files."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'class': 'form-control'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        # data is a list when multiple files are selected
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)


class MultiFileUploadForm(forms.Form):
    files = MultipleFileField(label='Select files to upload')


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
