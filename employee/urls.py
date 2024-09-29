from django.urls import path

from . import views

urlpatterns = [
    path('list', views.teacher_list, name='employee-list'),
]
