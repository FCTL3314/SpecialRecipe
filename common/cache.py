from django.core.cache import cache
from django.db.models import QuerySet


def get_cached_data_or_set_new(key: str, default: callable, timeout: int) -> QuerySet:
    """
    Checks if the cache exists for the given key. If not present,
    it caches the data obtained from calling the default function for
    timeout seconds.
    """
    data = cache.get(key)
    if not data:
        data = default()
        cache.set(key, data, timeout)
    return data
