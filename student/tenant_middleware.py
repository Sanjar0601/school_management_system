from django.utils.deprecation import MiddlewareMixin
from account.models import TenantUser, Tenant
import threading

_thread_locals = threading.local()

def get_current_tenant():
    return getattr(_thread_locals, 'tenant', None)


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            # Set the current user in thread-local storage
            threading.local().user = request.user

            try:
                tenant_user = TenantUser.objects.get(user=request.user)
                request.tenant = tenant_user.tenant  # Set tenant for current request
                threading.local().tenant = tenant_user.tenant  # Set tenant in thread-local storage
            except TenantUser.DoesNotExist:
                request.tenant = None  # No tenant found for the user
                threading.local().tenant = None
        else:
            request.tenant = None  # No tenant for unauthenticated users
            threading.local().tenant = None
            threading.local().user = None  # Clear user in thread-local storage
