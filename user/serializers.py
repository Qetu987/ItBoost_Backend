from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser, TeacherProfile, StudentProfile

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password',  'first_name', 'last_name', 'email', 'role', 'avatar']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            role=validated_data['role'],
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        # Add custom response data
        user_data = CustomUserSerializer(self.user).data
        data['user_data'] = user_data

        return data
    

class TeacherProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    bio = serializers.CharField()
    avatar = serializers.ImageField(source='user.avatar')
    role = serializers.CharField(source='user.role')

    class Meta:
        model = TeacherProfile
        fields = ['first_name', 'last_name', 'avatar', 'role', 'bio']


class StudentProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    age = serializers.IntegerField()
    avatar = serializers.ImageField(source='user.avatar')
    role = serializers.CharField(source='user.role')

    class Meta:
        model = TeacherProfile
        fields = ['first_name', 'last_name', 'avatar', 'role', 'bio']


class ProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    avatar = serializers.ImageField(source='user.avatar', allow_null=True, required=False)
    role = serializers.CharField(source='user.role', read_only=True)
    bio = serializers.CharField(allow_blank=True, required=False)
    age = serializers.IntegerField(required=False)

    class Meta:
        fields = ['first_name', 'last_name', 'avatar', 'role', 'bio', 'age']


    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.user.save()
        instance.save()

        return instance