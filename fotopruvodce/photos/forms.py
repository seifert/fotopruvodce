
from django import forms

from fotopruvodce.core.text import MARKDOWN_HELP_TEXT
from fotopruvodce.photos.models import Photo


class Evaluation(forms.Form):

    RATINGS = (
        tuple((j, j) for j in (str(i) for i in range(10, -1, -1))) +
        (('', 'Nebodovat'),)
    )

    content = forms.CharField(
        label="Komentář:", widget=forms.Textarea, required=False,
        help_text=MARKDOWN_HELP_TEXT)
    rating = forms.TypedChoiceField(
        label="Hodnocení:", choices=RATINGS, coerce=int,
        empty_value=None, required=False, widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        self.photo = kwargs.pop('photo', None)
        self.logged_user = kwargs.pop('logged_user', None)
        self.logged_user_rating = kwargs.pop('logged_user_rating', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        content = cleaned_data.get('content')
        rating = cleaned_data.get('rating')

        if content == '' and rating is None and not self.logged_user_rating:
            raise forms.ValidationError(
                'Vyplňte komentář, hodnocení, nebo obojí')

        if rating is not None and self.photo.user == self.logged_user:
            raise forms.ValidationError(
                'Nepřijde Vám divné bodovat si vlastní fotku?')

        return cleaned_data


class Add(forms.ModelForm):

    class Meta:
        model = Photo
        fields = [
            'title', 'description', 'active', 'section', 'thumbnail', 'photo']


class Edit(forms.ModelForm):

    class Meta:
        model = Photo
        fields = ['title', 'description', 'active', 'section']
