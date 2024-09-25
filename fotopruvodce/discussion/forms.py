from django import forms

from fotopruvodce.core.text import MARKDOWN_HELP_TEXT


class Comment(forms.Form):

    required_css_class = "form-required"

    title = forms.CharField(label="Předmět", max_length=128)
    content = forms.CharField(
        label="Komentář", widget=forms.Textarea, help_text=MARKDOWN_HELP_TEXT
    )


class Search(forms.Form):

    required_css_class = "form-required"

    q = forms.CharField(label="Co hledat", min_length=2)
