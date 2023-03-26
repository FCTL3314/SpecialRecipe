from django.core.cache import cache


class CacheMixin:
    @staticmethod
    def get_cached_data_or_new(key, default, timeout):
        data = cache.get(key)
        if not data:
            data = default()
            cache.set(key, data, timeout)
        return data
