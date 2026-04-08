from django.contrib import admin
from django.urls import path, include
from healthcheck import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('schedule/', views.schedule_view, name='schedule'),
    path('teams/', views.teams_view, name='teams'),
]