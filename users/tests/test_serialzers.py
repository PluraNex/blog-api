# users/tests/test_serializers.py
from django.test import TestCase
from django.contrib.auth.models import User
from users.serializers import UserSerializer, RegisterSerializer

class UserSerializerTest(TestCase):

    def setUp(self):
        """
        Configura um usuário para os testes de serialização.
        """
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
            first_name="Test",
            last_name="User"
        )

    def test_user_serializer(self):
        """
        Verifica se o `UserSerializer` serializa corretamente os dados de um usuário existente.
        """
        serializer = UserSerializer(instance=self.user)
        expected_data = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_active': self.user.is_active,
            'is_staff': self.user.is_staff,
        }
        self.assertEqual(serializer.data, expected_data)

class RegisterSerializerTest(TestCase):

    def setUp(self):
        """
        Configura os dados para criar um novo usuário com o `RegisterSerializer`.
        """
        self.user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "first_name": "New",
            "last_name": "User"
        }

    def test_register_serializer_create(self):
        """
        Verifica se o `RegisterSerializer` cria corretamente um novo usuário.
        """
        serializer = RegisterSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])

    def test_register_serializer_missing_fields(self):
        """
        Verifica se o `RegisterSerializer` falha quando faltam campos obrigatórios.
        """
        incomplete_data = {
            "username": "incompleteuser",
            # O campo "password" está ausente
            "email": "incompleteuser@example.com"
        }
        serializer = RegisterSerializer(data=incomplete_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_register_serializer_invalid_email(self):
        """
        Verifica se o `RegisterSerializer` falha quando um email inválido é fornecido.
        """
        invalid_email_data = self.user_data.copy()
        invalid_email_data['email'] = 'invalid-email'
        serializer = RegisterSerializer(data=invalid_email_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
