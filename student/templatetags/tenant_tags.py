from django import template
from account.models import TenantUser

register = template.Library()


@register.simple_tag(takes_context=True)
def has_teacher_profile(context):
    request = context['request']
    tenant_user = TenantUser.objects.filter(user=request.user, tenant=request.tenant).first()

    if tenant_user and tenant_user.teacher_profile:
        return True
    return False
