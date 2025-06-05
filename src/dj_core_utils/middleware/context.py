import threading
from django.utils.deprecation import MiddlewareMixin

_request_local = threading.local()


class CurrentUserMiddleware(MiddlewareMixin):
    """
    Middleware that stores the current user in a local thread
    Improved version with:
        - Guaranteed thread safety
        - Compatible with MiddlewareMixin
        - Automatic cleanup
    """

    def process_request(self, request):
        _request_local.user = getattr(request, 'user', None)
        return None

    def process_response(self, request, response):
        if hasattr(_request_local, 'user'):
            del _request_local.user
        return response


def get_current_user():
    """Get the current user from anywhere in the code"""
    return getattr(_request_local, 'user', None)
