from django.urls import path
from . import views

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('history/', views.HistoryListView.as_view(), name='history'),
    path('user/', views.CurrentUserView.as_view(), name='current_user'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('google-login/', views.google_login_view, name='google_login'),
]
