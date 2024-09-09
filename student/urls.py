from django.urls import path
from . import views

urlpatterns = [
    path('class-wise-student-registration', views.class_wise_student_registration, name='class-wise-student-registration'),
    path('student-registration', views.student_registration, name='student-registration'),
    path('student-list', views.student_list, name='student-list'),
    path('profile/<reg_no>', views.student_profile, name='student-profile'),
    path('delete/<reg_no>', views.student_delete, name='student-delete'),
    path('student-search/', views.BootStrapFilterView, name='student-search'),
    path('enrolled/', views.enrolled_student, name='enrolled-student'),
    path('enrolled-student/<reg>', views.student_enrolled, name='enrolled'),
    path('enrolled-student-list/', views.enrolled_student_list, name='enrolled-student-list'),
    path('group-registration', views.group_registration, name='group-registration'),
    path('group-list', views.group_list, name='group-list'),
    path('student-edit/<pk>', views.StudentDetailView.as_view(), name='student-detail')
    # path('sarch', views.BootStrapFilterView, name="filter")
]
