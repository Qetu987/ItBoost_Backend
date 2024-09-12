from rest_framework import generics
from .models import CustomUser
from .serializers import CustomUserSerializer, CustomTokenObtainPairSerializer, ProfileSerializer
from education.serializers import GroupDetailSerializer, GroupSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework import status
from django.shortcuts import get_object_or_404

from user.models import TeacherProfile, StudentProfile
from education.models import Group

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsModerator, IsTeacher


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


class ProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        user = self.request.user
        if user.role == 'teacher':
            return get_object_or_404(TeacherProfile, user=user)
        elif user.role == 'student':
            return get_object_or_404(StudentProfile, user=user)
        return None

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeacherGroupsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        group_id = request.query_params.get('group_id')

        teacher = request.user.teacherprofile
        groups = Group.objects.filter(lessons__teacher=teacher).distinct()
        group_serializer = GroupSerializer(groups, many=True)

        # Получаем первую группу
        if group_id:
            group = Group.objects.filter(id=group_id).first()
        else:
            group = groups.first() if groups.exists() else None
        group_detail_serializer = GroupDetailSerializer(group) if group else None

        return Response({
            'groups': group_serializer.data,
            'students': group_detail_serializer.data if group_detail_serializer else None
        })