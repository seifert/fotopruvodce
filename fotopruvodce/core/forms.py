
from django import forms


class UserEdit(forms.Form):

    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField()
    description = forms.CharField(widget=forms.Textarea, required=False)
    displayed_email = forms.CharField(max_length=128, required=False)


class UserSetPassword(forms.Form):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    current = forms.CharField(min_length=6, widget=forms.PasswordInput)
    new1 = forms.CharField(min_length=6, widget=forms.PasswordInput)
    new2 = forms.CharField(min_length=6, widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        current = cleaned_data.get("current")
        new1 = cleaned_data.get("new1")
        new2 = cleaned_data.get("new2")

        if current and not self.user.check_password(current):
            self.add_error('current', "Chybné aktuální heslo")

        if new1 and new2 and new1 != new2:
            self.add_error('new1', "Hesla se neshodují")
