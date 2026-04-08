from django.contrib import admin
from django.urls import path, include
from healthcheck import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard_view, name='dashboard'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('teams/', views.teams_view, name='teams'),
]