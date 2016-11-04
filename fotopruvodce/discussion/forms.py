
from django import forms


class Comment(forms.Form):

    title = forms.CharField(max_length=128)
    content = forms.CharField(widget=forms.Textarea)


class Search(forms.Form):

    q = forms.CharField(min_length=2)
