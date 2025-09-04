from django.urls import path
from .views import UserRegisterView, LogoutView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user-register'),
    path('logout/', LogoutView.as_view(), name='user-logout'),
]