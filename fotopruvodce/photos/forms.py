
from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat

from fotopruvodce.core.text import MARKDOWN_HELP_TEXT
from fotopruvodce.photos import models as photos_models
from fotopruvodce.workshops import models as workshop_models


class SeriesPhoto(forms.ModelForm):

    image = forms.ImageField(
        label="Další fotka do série:", required=False, help_text='Maximální '
        'povolené rozměry fotky jsou {}×{}px a velikost souboru do {}.'.format(
            settings.PHOTO_MAX_SIZE[0], settings.PHOTO_MAX_SIZE[1],
            filesizeformat(settings.PHOTO_MAX_UPLOAD_SIZE)))

    class Meta:
        model = photos_models.SeriesPhoto
        fields = ['image']


SeriesPhotoInline = forms.inlineformset_factory(
    photos_models.Photo, photos_models.SeriesPhoto, form=SeriesPhoto,
    can_delete=False, extra=2, max_num=2, validate_max=True)


WorkshopInline = forms.inlineformset_factory(
    photos_models.Photo, workshop_models.Workshop.photos.through,
    fields=('workshop',), extra=1)


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

    required_css_class = 'form-required'

    thumbnail = forms.ImageField(
        label="Náhled", required=False, help_text='Maximální povolené '
        'rozměry náhledu jsou {}×{}px a velikost souboru do {}. Pokud '
        'soubor nevyberete, bude náhled vygenerován automaticky.'.format(
            settings.THUMB_MAX_SIZE[0], settings.THUMB_MAX_SIZE[1],
            filesizeformat(settings.THUMB_MAX_UPLOAD_SIZE)))
    photo = forms.ImageField(
        label="Fotka", required=True, help_text='Maximální povolené '
        'rozměry fotky jsou {}×{}px a velikost souboru do {}.'.format(
            settings.PHOTO_MAX_SIZE[0], settings.PHOTO_MAX_SIZE[1],
            filesizeformat(settings.PHOTO_MAX_UPLOAD_SIZE)))

    class Meta:
        model = photos_models.Photo
        fields = [
            'title', 'description', 'active', 'section', 'thumbnail', 'photo']


class Edit(forms.ModelForm):

    required_css_class = 'form-required'

    class Meta:
        model = photos_models.Photo
        fields = ['title', 'description', 'active', 'section']
