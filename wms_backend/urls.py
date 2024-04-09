from django.contrib import admin
from django.urls import path
from users.views import userRegistration



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', userRegistration, name='userRegister'),

]
