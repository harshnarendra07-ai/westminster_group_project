from django.contrib import admin
from django.urls import path, include  # <-- Notice we added 'include' here

urlpatterns = [
    path('admin/', admin.site.urls),
    # This line tells Django: "Send all other web traffic to the healthcheck app's map!"
    path('', include('healthcheck.urls')), 
]

