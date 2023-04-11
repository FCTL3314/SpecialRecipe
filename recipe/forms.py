from django import forms


class SearchForm(forms.Form):
    search = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control me-2',
        'placeholder': 'Enter recipe name',
        'type': 'search',
        'aria-label': 'Search',
        'autocomplete': 'off',
    }))


class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Add a comment...',
        'type': 'text',
        'maxlength': '516',
    }))
