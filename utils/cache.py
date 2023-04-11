from django.core.cache import cache


def get_cached_data_or_set_new(key, default, timeout):
    data = cache.get(key)
    if not data:
        data = default()
        cache.set(key, data, timeout)
    return data
