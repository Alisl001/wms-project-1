from django.contrib import admin
from django.urls import path
from users.views import userRegistration, userAuthTokenLogin, userLogout, passwordResetRequest, passwordResetConfirm


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', userRegistration, name='userRegister'),
    path('api/login/', userAuthTokenLogin, name='userAuthTokenLogin'),
    path('api/logout/', userLogout, name='userLogout'),
    path('api/password-reset/request/', passwordResetRequest, name='passwordResetRequest'),
    path('api/password-reset/confirm/', passwordResetConfirm, name='passwordResetConfirm'),

]
