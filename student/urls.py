from django.urls import path
from . import views

urlpatterns = [
    path('student-registration', views.student_registration, name='student-registration'),
    path('student-list', views.student_list, name='student-list'),
    path('student-search/', views.BootStrapFilterView, name='student-search'),
    path('group-registration', views.group_registration, name='group-registration'),
    path('group-list', views.group_list, name='group-list'),
    path('student-edit/<pk>', views.StudentDetailView.as_view(), name='student-detail'),
    path('student/update/', views.student_update, name='student-update'),

    # path('sarch', views.BootStrapFilterView, name="filter")
]
