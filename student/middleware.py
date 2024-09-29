# middleware.py
import threading

# Thread-local storage for request
_request_local = threading.local()

def get_current_request():
    return getattr(_request_local, 'request', None)

class ThreadLocalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _request_local.request = request  # Set the current request in thread-local storage
        response = self.get_response(request)
        return response