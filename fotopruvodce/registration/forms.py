
from django import forms


class Register(forms.Form):

    use_required_attribute = False
    required_css_class = 'form-required'

    username = forms.CharField(
        label="Uživatelské jméno", max_length=150)
    email = forms.EmailField(
        label="E-mail")
    url = forms.URLField(
        label="URL", help_text="Nevyplňujte toto pole", required=False)
    signature = forms.CharField(
        widget=forms.HiddenInput, required=False)
    password1 = forms.CharField(
        label="Heslo", min_length=6, widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Ověření hesla", min_length=6, widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password1', "Hesla se neshodují")
