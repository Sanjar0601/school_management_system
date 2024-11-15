from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .forms import *
from account.models import TenantUser


def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            # Handle superusers
            if user.is_superuser:
                return redirect('home')  # Redirect superusers to a specific page

            # Check if the user belongs to multiple tenants
            tenants = TenantUser.objects.filter(user=user)
            if tenants.exists():
                if tenants.count() == 1:
                    # If only one tenant, automatically set it
                    request.tenant = tenants.first().tenant
                    return redirect('home')
                elif tenants.count() > 1:
                    # If multiple tenants, prompt the user to select one
                    return redirect('select_tenant')
            else:
                # Handle users with no tenants assigned
                return render(request, 'administration/login.html', {
                    'error': 'No tenant assigned to your account. Please contact support.'
                })
        else:
            return render(request, 'administration/login.html', {'error': 'Invalid login'})
    return render(request, 'administration/login.html')

def admin_logout(request):
    logout(request)
    return redirect('login')


