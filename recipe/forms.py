from django import forms


class SearchForm(forms.Form):
    search = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control me-2',
        'placeholder': 'Enter recipe name',
        'type': 'search',
        'aria-label': 'Search',
        'autocomplete': 'off',
    }))
