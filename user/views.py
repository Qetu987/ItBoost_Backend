from rest_framework import generics
from .models import CustomUser
from .serializers import CustomUserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsModerator

from rest_framework.decorators import permission_classes
from drf_yasg.utils import swagger_auto_schema


class RegisterView(generics.CreateAPIView):    
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated, IsModerator]
    serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = CustomUser.objects.get(username=response.data['username'])
        refresh = RefreshToken.for_user(user)
        response.data['refresh'] = str(refresh)
        response.data['access'] = str(refresh.access_token)
        return response
    

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
@swagger_auto_schema(
    operation_id='current_user_view',
    operation_description='Retrieves the current user\'s information.',
    security=[{'bearerAuth': []}]
)
@permission_classes([IsAuthenticated])
class CurrentUserView(APIView):
    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)
