from django import forms

class PostSearchForm(forms.Form):
    search_term = forms.CharField(label = "search word")

class PrivatePostSearchForm(forms.Form):
    search_term = forms.CharField(label = "search word (private posts)")

class TagSearchForm(forms.Form):
    search_term = forms.CharField(label = "search tags")

class AuthorSearchForm(forms.Form):
    search_term = forms.CharField(label = "search author")
