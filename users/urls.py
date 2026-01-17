from django.contrib import admin
from django.urls import path,include
from users.views import *

urlpatterns = [
    path("signup/",UserSignupView.as_view(),name="signup"),
    path('login/',LoginView.as_view(),name="login"),
    path('logout/',LogoutView.as_view(),name="logout"),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("contact/", ContactCreateView.as_view(), name="contact"),

]
