from functools import wraps

from django.shortcuts import HttpResponseRedirect
from django.urls import reverse


def logout_required(function, redirect_url='accounts:profile'):
    """
    Decorator for views that checks that the user is logged out, redirecting
    to the profile page.
    """

    @wraps(function)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return function(request, *args, **kwargs)
        return HttpResponseRedirect(reverse(redirect_url, args={request.user.slug}))

    return wrapper
