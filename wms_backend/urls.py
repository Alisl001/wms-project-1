from django.contrib import admin
from django.urls import path
from users.views import userRegistration, userAuthTokenLogin, userLogout


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', userRegistration, name='userRegister'),
    path('api/login/', userAuthTokenLogin, name='userAuthTokenLogin'),
    path('api/logout/', userLogout, name='userLogout'),

]
