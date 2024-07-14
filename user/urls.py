from django.urls import path
from user.views import RegisterView, ProtectedModeratorAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('moderator-protected/', ProtectedModeratorAPIView.as_view(), name='moderator_protected_api'),
]