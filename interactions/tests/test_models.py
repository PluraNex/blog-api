# interactions/tests/test_models.py

from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, transaction
from interactions.models import UserInteraction, InteractionType
from interactions.tests.base_test import BaseInteractionTest
from userprofile.models import UserProfile

class UserInteractionTests(BaseInteractionTest):

    def test_create_follow_interaction(self):
        """
        Verifica a criação de uma interação do tipo FOLLOW.
        Espera-se que a interação seja associada ao usuário e ao perfil de usuário seguido,
        e que o `content_object` seja o perfil de usuário.
        """
        profile_content_type = ContentType.objects.get_for_model(UserProfile)
        interaction = UserInteraction.objects.create(
            user=self.user,
            interaction_type=InteractionType.FOLLOW,
            content_type=profile_content_type,
            object_id=self.user_profile.id
        )
        
        # Validações
        self.assertEqual(interaction.interaction_type, InteractionType.FOLLOW)
        self.assertEqual(interaction.user, self.user)
        self.assertEqual(interaction.content_object, self.user_profile)

    def test_create_like_interaction(self):
        """
        Verifica a criação de uma interação do tipo LIKE em um artigo.
        Espera-se que a interação seja associada ao usuário e ao artigo curtido,
        e que o `content_object` seja o artigo.
        """
        article_content_type = ContentType.objects.get_for_model(self.article)
        interaction = UserInteraction.objects.create(
            user=self.user,
            interaction_type=InteractionType.LIKE,
            content_type=article_content_type,
            object_id=self.article.id
        )

        # Validações
        self.assertEqual(interaction.interaction_type, InteractionType.LIKE)
        self.assertEqual(interaction.user, self.user)
        self.assertEqual(interaction.content_object, self.article)

    def test_unique_constraint_on_interactions(self):
        """
        Testa a restrição de unicidade de interações.
        Espera-se que uma interação do mesmo tipo entre o mesmo usuário e o mesmo objeto
        não possa ser duplicada. A tentativa de duplicação deve gerar uma exceção.
        """
        article_content_type = ContentType.objects.get_for_model(self.article)
        
        # Criação da interação inicial
        UserInteraction.objects.create(
            user=self.user,
            interaction_type=InteractionType.LIKE,
            content_type=article_content_type,
            object_id=self.article.id
        )
        
        # Tentativa de criar uma interação duplicada e verificação da exceção
        with transaction.atomic():
            with self.assertRaises(IntegrityError, msg="A violação de restrição de unicidade deve gerar um IntegrityError"):
                UserInteraction.objects.create(
                    user=self.user,
                    interaction_type=InteractionType.LIKE,
                    content_type=article_content_type,
                    object_id=self.article.id
                )
