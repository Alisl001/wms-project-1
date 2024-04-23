from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from users.views import passwordResetCodeCheck, userRegistration, userAuthTokenLogin, userLogout, passwordResetRequest, passwordResetCodeCheck, passwordResetConfirm, retrieveUserById, myDetails, changeMyPassword, updateUserInfo, deleteMyAccount, deleteUserById, showStaffMembers, grantStaffPermission


urlpatterns = [
    path('admin/', admin.site.urls),

    # User Management APIs
    path('api/register/', userRegistration, name='userRegister'),
    path('api/login/', userAuthTokenLogin, name='userAuthTokenLogin'),
    path('api/logout/', userLogout, name='userLogout'),
    path('api/password-reset/request/', passwordResetRequest, name='passwordResetRequest'),
    path('api/password-reset/code-check/', passwordResetCodeCheck, name='passwordResetCodeCheck'),
    path('api/password-reset/confirm/', passwordResetConfirm, name='passwordResetConfirm'),
    path('api/users/<int:id>/', retrieveUserById, name='userDetail'),
    path('api/users/my-details/', myDetails, name='myDetails'),
    path('api/user/change-password/', changeMyPassword, name='changePassword'),
    path('api/user/update-info/', updateUserInfo, name='updateUserInfo'),
    path('api/user/delete-my-account/', deleteMyAccount, name='deleteMyAccount'),
    path('api/users/delete/<int:id>/', deleteUserById, name='deleteUserAccount'),
    path('api/users/staff/', showStaffMembers, name='showStaffMembers'),
    path('api/users/grant-permission/<int:staff_id>/', grantStaffPermission, name='grantStaffPermission'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
