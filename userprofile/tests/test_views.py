import os
import shutil
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from userprofile.models import UserProfile
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


TEST_MEDIA_ROOT = 'test_media/'

@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ProfileDetailViewTest(TestCase):
    PROFILE_URL = "/api/v1/profiles/"

    def setUp(self):
        """
        Configura um usuário e seu perfil para os testes, além de preparar o cliente autenticado.
        """
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.profile = self.user.userprofile
        self.profile.bio = "Test Bio"
        self.profile.location = "Test Location"
        self.profile.gender = "M"
        self.profile.save()

        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def tearDown(self):
        """
        Remove o diretório de mídia de teste após a execução dos testes.
        """
        self.user.delete()
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)

    def test_get_user_profile(self):
        """
        Testa a recuperação do perfil do usuário autenticado.
        Deve retornar o status HTTP 200 OK e os detalhes do perfil.
        """
        response = self.client.get(self.PROFILE_URL)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['bio'], "Test Bio")
        self.assertEqual(response.data['location'], "Test Location")
        self.assertEqual(response.data['gender'], "M")

    def test_get_user_profile_unauthenticated(self):
        """
        Testa a tentativa de acessar o perfil sem autenticação.
        Deve retornar o status HTTP 401 Unauthorized.
        """
        self.client.credentials()
        response = self.client.get(self.PROFILE_URL)
        
        self.assertEqual(response.status_code, 401)

    def test_update_user_profile(self):
        """
        Testa a atualização do perfil do usuário autenticado.
        Deve retornar o status HTTP 200 OK e refletir as mudanças feitas.
        """
        image = BytesIO()
        Image.new("RGB", (100, 100)).save(image, "JPEG")
        image.seek(0)
        image.name = 'test_image.jpg'

        response = self.client.put(
            self.PROFILE_URL,
            {
                "bio": "New Bio",
                "location": "New Location",
                "gender": "M",
                "profile_picture": SimpleUploadedFile(image.name, image.read(), content_type='image/jpeg')
            },
            format='multipart'
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['bio'], "New Bio")
        self.assertEqual(response.data['location'], "New Location")
        self.assertIn('test_image', response.data['profile_picture'])

        updated_profile = UserProfile.objects.get(user=self.user)
        if updated_profile.profile_picture:
            file_path = updated_profile.profile_picture.path
            self.assertTrue(os.path.exists(file_path))

    def test_update_user_profile_unauthenticated(self):
        """
        Testa a tentativa de atualizar o perfil sem autenticação.
        Deve retornar o status HTTP 401 Unauthorized.
        """
        self.client.credentials()
        
        response = self.client.put(
            self.PROFILE_URL,
            {
                "bio": "New Bio",
                "location": "New Location",
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 401)

    def test_update_user_profile_invalid_data(self):
        """
        Testa a atualização do perfil com dados inválidos.
        Deve retornar o status HTTP 400 Bad Request e indicar o campo inválido.
        """
        response = self.client.put(
            self.PROFILE_URL,
            {
                "bio": "",
                "location": "New Location",
                "gender": "Invalid Gender"
            },
            format='multipart'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("gender", response.data)
