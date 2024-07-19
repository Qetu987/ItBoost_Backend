from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CustomUser

class ProtectedViewTests(APITestCase):
    def setUp(self):
        self.moderator = CustomUser.objects.create_user(username='moderator', password='testpassword', role='moderator')
        self.student = CustomUser.objects.create_user(username='student', password='testpassword', role='student')
        self.token_url = reverse('token_obtain_pair')
        self.protected_url = reverse('auth_register')

        response = self.client.post(self.token_url, {'username': 'moderator', 'password': 'testpassword'}, format='json')
        self.moderator_access_token = response.data['access']

        response = self.client.post(self.token_url, {'username': 'student', 'password': 'testpassword'}, format='json')
        self.student_access_token = response.data['access']

    def test_moderator_protected_view_without_token(self):
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_moderator_protected_view_with_student_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.student_access_token)
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_protected_view_with_moderator_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.moderator_access_token)
        response = self.client.post(self.protected_url, data={'username': 'newuser', 'password': 'newpassword', "email": 'test@gmail.com', "role": 'student'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)