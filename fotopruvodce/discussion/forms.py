
from django import forms

from fotopruvodce.core.text import MARKDOWN_HELP_TEXT


class Comment(forms.Form):

    title = forms.CharField(
        label="Předmět:", max_length=128)
    content = forms.CharField(
        label="Komentář:", widget=forms.Textarea, help_text=MARKDOWN_HELP_TEXT)


class Search(forms.Form):

    q = forms.CharField(
        label="Co hledat:", min_length=2)
