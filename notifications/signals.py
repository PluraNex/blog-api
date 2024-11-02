from django.db.models.signals import post_save
from django.dispatch import receiver
from interactions.models import UserInteraction, InteractionType
from notifications.models import NotificationInteraction
from userprofile.models import UserProfile
from articles.models import Article

@receiver(post_save, sender=UserInteraction)
def create_interaction_notification(sender, instance, created, **kwargs):
    if not created:
        return

    # Verifica se a interação é uma curtida
    if instance.interaction_type == InteractionType.LIKE:
        # Confirma que o objeto curtido é um artigo
        if isinstance(instance.content_object, Article):
            article = instance.content_object
            author_profile = article.author  # O autor do artigo é um UserProfile

            # Verifica se o autor deseja notificações de curtidas
            if author_profile.is_author and author_profile.notification_settings.notify_on_like:
                message = f"{instance.user.username} liked your article '{article.title}'."
                NotificationInteraction.objects.create(
                    user=author_profile.user,  # O usuário do autor
                    message=message,
                    interaction_type=InteractionType.LIKE
                )

    # Verifica se a interação é um novo seguidor
    elif instance.interaction_type == InteractionType.FOLLOW:
        # Confirma que o objeto seguido é um perfil de usuário
        if isinstance(instance.content_object, UserProfile):
            followed_user_profile = instance.content_object

            # Verifica se o usuário seguido deseja receber notificações de novos seguidores
            if followed_user_profile.notification_settings.notify_on_new_follower:
                message = f"{instance.user.username} started following you."
                NotificationInteraction.objects.create(
                    user=followed_user_profile.user,
                    message=message,
                    interaction_type=InteractionType.FOLLOW
                )
                
