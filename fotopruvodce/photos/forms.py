
from django import forms

from fotopruvodce.photos.models import Photo


class Evaluation(forms.Form):

    RATINGS = tuple((j, j) for j in (str(i) for i in range(10, -1, -1))) + (('', 'Nebodovat'),)

    content = forms.CharField(widget=forms.Textarea, required=False)
    rating = forms.TypedChoiceField(
        choices=RATINGS, coerce=int, empty_value=None,
        required=False, widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        self.logged_user = kwargs.pop('logged_user', None)
        self.photo_user = kwargs.pop('photo_user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        rating = cleaned_data.get('rating')

        if content == '' and rating is None:
            raise forms.ValidationError('Vyplňte komentář, hodnocení, nebo obojí')

        if rating is not None and self.photo_user == self.logged_user:
            raise forms.ValidationError('Nepřijde Vám divné bodovat si vlastní fotku?')


class Add(forms.ModelForm):

    class Meta:
        model = Photo
        fields = ['title', 'description', 'active', 'section', 'thumbnail', 'photo']


class Edit(forms.ModelForm):

    class Meta:
        model = Photo
        fields = ['title', 'description', 'active', 'section']
