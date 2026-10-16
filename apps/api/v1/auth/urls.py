from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.api.v1.auth import views

urlpatterns = [
    path("login/", views.LoginAPIView.as_view(), name="login"),
    path("login/confirm/", views.LoginConfirmAPIView.as_view(), name="login_confirm"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # path("register/", views.UserRegisterAPIView.as_view(), name="register"),
    # path("register/confirm/", views.UserRegisterConfirmAPIView.as_view(), name="register_confirm"),

    # path("reset-password/", views.ResetPasswordAPIView.as_view(), name="reset_password"),
    # path("reset-password/confirm/", views.ResetPasswordConfirmAPIView.as_view(), name="reset_password_confirm"),
    # path("reset-password/complete/", views.ResetPasswordCompleteAPIView.as_view(), name="reset_password_complete"),

    # path("change-phone/", views.ChangePhoneNumberAPIView.as_view(), name="change_phone_number"),
    # path("change-phone/confirm/", views.ChangePhoneNumberConfirmAPIView.as_view(), name="change_phone_number_confirm"),

    # path("change-password/", views.ChangePasswordAPIView.as_view(), name="change_password"),
    # path("delete-account/", views.DeleteAccountAPIView.as_view(), name="delete_account"),
    # path("delete-account/confirm/", views.DeleteAccountConfirmAPIView.as_view(), name="delete_account_confirm"),
]
