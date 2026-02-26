from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Jobs
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/create/', views.job_create, name='job_create'),
    path('jobs/<int:job_id>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<int:job_id>/delete/', views.job_delete, name='job_delete'),
    path('jobs/<int:job_id>/apply/', views.job_apply, name='job_apply'),
    
    # Applications
    path('applications/', views.application_list, name='application_list'),
    path('applications/<int:app_id>/approve/', views.application_approve, name='application_approve'),
    path('applications/<int:app_id>/reject/', views.application_reject, name='application_reject'),
    
    # Work Hours
    path('hours/log/', views.work_hour_log, name='work_hour_log'),
    path('hours/', views.work_hour_list, name='work_hour_list'),
    path('hours/<int:hour_id>/approve/', views.work_hour_approve, name='work_hour_approve'),
    path('hours/<int:hour_id>/reject/', views.work_hour_reject, name='work_hour_reject'),
    
    # Feedbacks
    path('feedbacks/', views.feedback_list, name='feedback_list'),
    path('feedbacks/<int:student_id>/create/', views.feedback_create, name='feedback_create'),
    
    # Students
    path('students/', views.student_list, name='student_list'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
]
