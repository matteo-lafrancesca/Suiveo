from django.urls import path
from .views import LoginView, MeView, CreateUserView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('me/', MeView.as_view(), name='me'),
    path('users/create/', CreateUserView.as_view(), name='create_user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
