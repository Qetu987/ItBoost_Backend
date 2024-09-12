from django.urls import path
from user.views import RegisterView, CustomTokenObtainPairView, ProfileView, TeacherGroupsView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),

    path('student_list/', TeacherGroupsView.as_view(), name='student_list'),
]