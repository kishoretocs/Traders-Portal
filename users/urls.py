# users/urls.py
from django.urls import path
from .views import RegisterView,LoginView,LogoutView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('auth/logout/', LogoutView.as_view()),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # path('login/firebase/', FirebaseLoginView.as_view(), name='firebase-login'),
    # path("login/", firebase_login_page, name="firebase-login-page"),

]
