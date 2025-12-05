"""
URL configuration for predictions app
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('predict/', views.predict_view, name='predict'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('history/', views.history_view, name='history'),
    path('patient/<str:patient_id>/', views.patient_detail_view, name='patient_detail'),
    # Admin-only routes (using 'manage' prefix to avoid conflict with Django admin)
    path('manage/health-workers/', views.health_workers_view, name='health_workers'),
    path('manage/health-worker/<int:user_id>/', views.health_worker_detail_view, name='health_worker_detail'),
    path('manage/patients/', views.patients_management_view, name='patients_management'),
    path('manage/users/', views.users_management_view, name='users_management'),
    path('manage/audit-logs/', views.audit_logs_view, name='audit_logs'),
    path('manage/analytics/', views.analytics_charts_view, name='analytics'),
    path('manage/analytics/data/', views.analytics_data_api, name='analytics_data'),
    path('manage/export/csv/', views.export_csv_view, name='export_csv'),
]

