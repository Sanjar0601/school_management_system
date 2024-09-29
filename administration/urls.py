from django.urls import path
from . import views


urlpatterns = [
    path('login', views.custom_login_view, name='login'),
    path('logout', views.admin_logout, name='logout'),
]
