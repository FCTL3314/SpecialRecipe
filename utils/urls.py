def is_url_allowed(url_pattern, allowed_urls):
    """
    Allows to exclude unnecessary routes, checks whether the received
    route matches the allowed ones.
    """
    for url in allowed_urls:
        match = url_pattern.resolve(url)
        if match:
            return True
    return False
