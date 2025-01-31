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
    path('group-students/<int:pk>/', views.GroupStudentsView.as_view(), name='group-students'),
    path('student/save-attendance/', views.SaveAttendanceView.as_view(), name='save-attendance'),
    path('attendace_report', views.attendance_table, name='report'),
    path('group/edit/', views.edit_group_view, name='edit_group'),
    path('balance_update', views.balance_update, name='balance_update'),
    path('expenses/add/', views.add_expense_view, name='add_expense'),
    path('expense_list', views.ExpenseListView.as_view(), name='expense_list'),
    path('delete-group/', views.delete_group, name='delete-group'),
    path('ajax/load-groups', views.load_groups, name='ajax-load-groups'),
    path('expense-update', views.update_expense, name='expense_update')

]
