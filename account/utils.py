# utils/helpers.py (or any file you use for utilities)
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse

def build_full_url(request, view_name, kwargs=None, query_params=None):
    """
    Returns a full absolute URL (with protocol and domain) to a Django named view.
    
    - view_name: The name used in reverse() (e.g. 'account:sms_status_callback')
    - kwargs: Optional view kwargs
    - query_params: Optional dict of query parameters
    """
    current_site = get_current_site(request)
    domain = current_site.domain
    protocol = 'https' if request.is_secure() else 'http'
    path = reverse(view_name, kwargs=kwargs)
    
    url = f"{protocol}://{domain}{path}"
    
    if query_params:
        from urllib.parse import urlencode
        url += f"?{urlencode(query_params)}"
    
    return url
