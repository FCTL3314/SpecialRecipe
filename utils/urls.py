from typing import List

from django.urls import URLPattern


def filter_urls(urls: List[URLPattern], allowed_names: List[str]) -> List[URLPattern]:
    """
    Filters a list of URL patterns based on their name.

    Parameters:
        urls : A list of URL patterns to filter.
        allowed_names : A list of allowed URL names.

    Returns:
        List[URLPattern] : A filtered list of URL patterns with names in the allowed_names list.
    """
    filtered_urls = list(
        filter(lambda url: url.name in allowed_names, urls),
    )
    return filtered_urls
