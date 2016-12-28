
from django import forms


class Comment(forms.Form):

    title = forms.CharField(
        label="Předmět:", max_length=128)
    content = forms.CharField(
        label="Komentář:", widget=forms.Textarea)


class Search(forms.Form):

    q = forms.CharField(
        label="Co hledat:", min_length=2)
