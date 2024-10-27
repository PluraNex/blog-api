from rest_framework.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import User
from users.serializers import CustomTokenObtainPairSerializer, UserSerializer, RegisterSerializer

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
        
        # Criando o usuário para o teste
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123"
        )

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

    def test_token_serializer_with_missing_username_and_email(self):
        """
        Testa a validação do `CustomTokenObtainPairSerializer` quando tanto o `username` quanto o `email` estão ausentes.
        Deve lançar um ValidationError com a mensagem "Credenciais de login inválidas."
        """
        serializer = CustomTokenObtainPairSerializer(data={'password': 'password123'})
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Credenciais de login inválidas.", str(context.exception))

    def test_token_serializer_with_email_instead_of_username(self):
        """
        Testa o `CustomTokenObtainPairSerializer` usando o `email` para autenticação.
        Deve retornar tokens de acesso e refresh ao autenticar com sucesso.
        """
        data = {'email': 'testuser@example.com', 'password': 'password123'}
        serializer = CustomTokenObtainPairSerializer(data=data)
        
        self.assertTrue(serializer.is_valid(raise_exception=True))
        
        tokens = serializer.validated_data

        self.assertIn('refresh', tokens)
        self.assertIn('access', tokens)

    def test_token_serializer_invalid_credentials(self):
        """
        Testa o `CustomTokenObtainPairSerializer` com credenciais inválidas.
        Deve lançar um ValidationError com a mensagem "Credenciais de login inválidas."
        """
        serializer = CustomTokenObtainPairSerializer(data={'username': 'testuser', 'password': 'wrongpassword'})
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Credenciais de login inválidas.", str(context.exception))

    def test_token_serializer_with_nonexistent_email(self):
        """
        Testa o `CustomTokenObtainPairSerializer` com um email que não existe no sistema.
        Deve lançar um ValidationError com a mensagem "Credenciais de login inválidas."
        """
        data = {'email': 'nonexistent@example.com', 'password': 'password123'}
        serializer = CustomTokenObtainPairSerializer(data=data)
        
        with self.assertRaises(ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Credenciais de login inválidas.", str(context.exception))

