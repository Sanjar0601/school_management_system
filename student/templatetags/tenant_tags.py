from django import template
from account.models import TenantUser

register = template.Library()


@register.simple_tag(takes_context=True)
def has_teacher_profile(context):
    request = context.get('request')

    # Ensure the request object exists and the user is authenticated
    if not request or not request.user.is_authenticated:
        return False

    # Ensure the tenant is set in the request
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return False

    # Fetch the TenantUser for the current user and tenant
    tenant_user = TenantUser.objects.filter(user=request.user, tenant=tenant).first()

    # Check if the tenant_user has a teacher_profile
    if tenant_user and hasattr(tenant_user, 'teacher_profile') and tenant_user.teacher_profile:
        return True

    return False