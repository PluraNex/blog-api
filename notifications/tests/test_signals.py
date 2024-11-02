# notifications/tests/test_signals.py
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from interactions.models import UserInteraction, InteractionType
from notifications.models import NotificationInteraction
from notifications.tests.base_test import BaseNotificationTest
from userprofile.models import UserProfile
from articles.models import Article

class NotificationSignalTests(BaseNotificationTest):

    def test_follow_interaction_creates_notification(self):
        """
        Verifica se uma notificação é criada quando uma interação do tipo FOLLOW ocorre.
        Espera-se que uma notificação seja criada para o usuário seguido.
        """
        profile_content_type = ContentType.objects.get_for_model(UserProfile)

        # Criação da interação de seguir
        UserInteraction.objects.create(
            user=self.user,  # Usuário interagindo
            interaction_type=InteractionType.FOLLOW,
            content_type=profile_content_type,
            object_id=self.user_profile.id,
        )

        # Verifica se a notificação foi criada
        notification = NotificationInteraction.objects.filter(
            user=self.user,
            interaction_type=InteractionType.FOLLOW,
            message=f"{self.user.username} started following you."
        ).first()

        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.interaction_type, InteractionType.FOLLOW)

    def test_like_interaction_no_notification_when_disabled(self):
        """
        Verifica que nenhuma notificação é criada quando o autor desativa notificações de curtidas.
        """
        # Desabilita notificações de curtidas para o autor
        self.notification_settings.notify_on_like = False
        self.notification_settings.save()

        article_content_type = ContentType.objects.get_for_model(Article)

        # Criação da interação de curtida
        UserInteraction.objects.create(
            user=self.user,  # Usuário interagindo
            interaction_type=InteractionType.LIKE,
            content_type=article_content_type,
            object_id=self.article.id,
        )

        # Verifica que nenhuma notificação foi criada
        notifications = NotificationInteraction.objects.filter(
            user=self.user,
            interaction_type=InteractionType.LIKE
        )
        self.assertEqual(notifications.count(), 0)

    def test_follow_interaction_no_notification_when_disabled(self):
        """
        Verifica que nenhuma notificação é criada quando o autor desativa notificações de novos seguidores.
        """
        # Desabilita notificações de novos seguidores para o autor
        self.notification_settings.notify_on_new_follower = False
        self.notification_settings.save()

        profile_content_type = ContentType.objects.get_for_model(UserProfile)

        # Criação da interação de seguir
        UserInteraction.objects.create(
            user=self.user,  # Usuário interagindo
            interaction_type=InteractionType.FOLLOW,
            content_type=profile_content_type,
            object_id=self.user_profile.id,
        )

        # Verifica que nenhuma notificação foi criada
        notifications = NotificationInteraction.objects.filter(
            user=self.user,
            interaction_type=InteractionType.FOLLOW
        )
        self.assertEqual(notifications.count(), 0)

    def test_like_interaction_creates_notification(self):
        """
        Verifica se uma notificação é criada quando uma interação do tipo LIKE ocorre.
        Espera-se que uma notificação seja criada para o autor do artigo.
        """
        article_content_type = ContentType.objects.get_for_model(Article)

        interactor_user, _ = User.objects.get_or_create(username='interactor_user', defaults={'password': 'test_password'})
        
        self.notification_settings.notify_on_like = True
        self.notification_settings.save()

        UserInteraction.objects.create(
            user=interactor_user,
            interaction_type=InteractionType.LIKE,
            content_type=article_content_type,
            object_id=self.article.id,
        )

        notification = NotificationInteraction.objects.filter(
            user=self.user,  # O autor do artigo
            interaction_type=InteractionType.LIKE,
            message=f"{interactor_user.username} liked your article '{self.article.title}'."
        ).first()

        self.assertIsNotNone(notification, "A notificação deveria ter sido criada, mas não foi encontrada.")
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.interaction_type, InteractionType.LIKE)


