from django.contrib import admin
from django.urls import path
from users.views import userRegistration, userAuthTokenLogin, userLogout, passwordResetRequest, passwordResetConfirm, retrieveUserById, myDetails, changeMyPassword, updateUserInfo, deleteMyAccount, deleteUserById, showStaffMembers


urlpatterns = [
    path('admin/', admin.site.urls),

    # User Management APIs
    path('api/register/', userRegistration, name='userRegister'),
    path('api/login/', userAuthTokenLogin, name='userAuthTokenLogin'),
    path('api/logout/', userLogout, name='userLogout'),
    path('api/password-reset/request/', passwordResetRequest, name='passwordResetRequest'),
    path('api/password-reset/confirm/', passwordResetConfirm, name='passwordResetConfirm'),
    path('api/users/<int:id>/', retrieveUserById, name='userDetail'),
    path('api/users/my-details/', myDetails, name='myDetails'),
    path('api/user/change-password/', changeMyPassword, name='changePassword'),
    path('api/user/update-info/', updateUserInfo, name='updateUserInfo'),
    path('api/user/delete-my-account/', deleteMyAccount, name='deleteMyAccount'),
    path('api/users/delete/<int:id>/', deleteUserById, name='deleteUserAccount'),
    path('api/users/staff/', showStaffMembers, name='showStaffMembers'),

]
