from django import forms

class PostSearchForm(forms.Form):
    search_term = forms.CharField(label = "Search Word")

class PrivatePostSearchForm(forms.Form):
    search_term = forms.CharField(label = "Search Word")
