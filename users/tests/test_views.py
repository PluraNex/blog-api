from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

class UserViewSetTest(TestCase):
    BASE_URL = "/api/v1/users/"
    CREATE_USER_DATA = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword123",
        "first_name": "New",
        "last_name": "User"
    }

    def setUp(self):
        """
        Configura dois usuários para os testes:
        - Um usuário normal para testar as permissões e operações de um usuário comum.
        - Um usuário administrador para testar operações que requerem permissões administrativas.
        """
        self.user = User.objects.create_user(username="testuser", password="password123", email="testuser@example.com")
        self.admin_user = User.objects.create_superuser(username="adminuser", password="adminpassword", email="admin@example.com")
        self.client = APIClient()

    def authenticate_user(self):
        """Autentica o cliente como um usuário normal utilizando JWT."""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def authenticate_admin(self):
        """Autentica o cliente como um administrador utilizando JWT."""
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    # Testes de Criação
    def test_create_user(self):
        """
        Verifica se um novo usuário pode ser criado com sucesso.
        Deve retornar o status HTTP 201 CREATED e os detalhes do usuário recém-criado.
        """
        response = self.client.post(self.BASE_URL, self.CREATE_USER_DATA, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], self.CREATE_USER_DATA['username'])
        self.assertEqual(response.data['email'], self.CREATE_USER_DATA['email'])
    

    def test_create_user_missing_email(self):
        """
        Verifica se a criação de um novo usuário falha quando o campo 'email' está ausente.
        Deve retornar o status HTTP 400 BAD REQUEST.
        """
        incomplete_data = {"username": "incompleteuser", "password": "password123"}
        response = self.client.post(self.BASE_URL, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_create_user_missing_password(self):
        """
        Verifica se a criação de um novo usuário falha quando o campo 'password' está ausente.
        Deve retornar o status HTTP 400 BAD REQUEST.
        """
        incomplete_data = {"username": "incompleteuser", "email": "incomplete@example.com"}
        response = self.client.post(self.BASE_URL, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    # Testes de Listagem
    def test_list_users_as_admin(self):
        """
        Verifica se um administrador pode listar todos os usuários.
        Deve retornar o status HTTP 200 OK.
        """
        self.authenticate_admin()
        response = self.client.get(self.BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    

    def test_list_users_as_normal_user(self):
        """
        Verifica se um usuário normal NÃO pode listar todos os usuários.
        Deve retornar o status HTTP 403 FORBIDDEN.
        """
        self.authenticate_user()
        response = self.client.get(self.BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Testes de Detalhe e Atualização
    def test_retrieve_own_user_detail(self):
        """
        Verifica se um usuário autenticado pode ver seus próprios detalhes.
        Deve retornar HTTP 200 OK e os detalhes corretos do usuário.
        """
        self.authenticate_user()
        response = self.client.get(f'{self.BASE_URL}{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_retrieve_another_user_detail_forbidden(self):
        """
        Verifica se um usuário autenticado NÃO pode acessar os detalhes de outro usuário.
        Deve retornar HTTP 403 FORBIDDEN.
        """
        self.authenticate_user()
        response = self.client.get(f'{self.BASE_URL}{self.admin_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user_detail(self):
        """
        Verifica se um usuário autenticado pode atualizar suas próprias informações.
        Deve retornar o status HTTP 200 OK e refletir as atualizações feitas.
        """
        self.authenticate_user()
        update_data = {
            "username": "updateduser",
            "email": "updateduser@example.com",
            "first_name": "Updated",
            "last_name": "User"
        }
        response = self.client.put(f'{self.BASE_URL}{self.user.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], update_data['username'])
        self.assertEqual(response.data['email'], update_data['email'])

    def test_update_another_user_detail_forbidden(self):
        """
        Verifica se um usuário autenticado NÃO pode atualizar as informações de outro usuário.
        Deve retornar HTTP 403 FORBIDDEN.
        """
        self.authenticate_user()
        update_data = {
            "username": "unauthorizedupdate",
            "email": "unauthorized@example.com"
        }
        response = self.client.put(f'{self.BASE_URL}{self.admin_user.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Testes de Exclusão
    def test_destroy_user_as_admin(self):
        """
        Verifica se um administrador pode excluir um usuário.
        Deve retornar HTTP 204 NO CONTENT.
        """
        self.authenticate_admin()
        response = self.client.delete(f'{self.BASE_URL}{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_destroy_user_as_normal_user(self):
        """
        Verifica se um usuário normal NÃO pode excluir um usuário.
        Deve retornar HTTP 403 FORBIDDEN.
        """
        self.authenticate_user()
        response = self.client.delete(f'{self.BASE_URL}{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)





