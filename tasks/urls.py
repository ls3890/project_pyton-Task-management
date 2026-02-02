from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('setup/', views.setup_profile, name='setup_profile'),
    path('', views.task_list, name='task_list'),
    path('create/', views.create_task, name='create_task'),
    path('edit/<int:task_id>/', views.edit_task, name='edit_task'),
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),
    path('assign/<int:task_id>/', views.assign_task, name='assign_task'),
    path('status/<int:task_id>/', views.change_status, name='change_status'),
    path('logout/', views.logout_view, name='logout'),
]