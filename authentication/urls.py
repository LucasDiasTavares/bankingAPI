from django.urls import path
from .views import (
    RegisterView,
    VerifyEmail,
    LoginAPIView,
    PasswordTokenCheckAPI,
    ResetPasswordEmailAPIView,
    SetNewPasswordAPIView,
    LogoutAPIView,
    AuthUserAPIView,
    UserAddressUpdateAPIView)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('user/', AuthUserAPIView.as_view(), name="user-data"),
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginAPIView.as_view(), name="login"),
    path('logout/', LogoutAPIView.as_view(), name="logout"),
    path('email-verify/', VerifyEmail.as_view(), name="email-verify"),
    path('token/refresh', TokenRefreshView.as_view(), name="token-refresh"),
    path('request-reset-password/', ResetPasswordEmailAPIView.as_view(), name="request-reset-password"),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name="password-reset-confirm"),
    path('password-reset-complete/', SetNewPasswordAPIView.as_view(), name="password-reset-complete"),
    path('user-address-update/<int:pk>/', UserAddressUpdateAPIView.as_view(), name="user-address-update"),
]
