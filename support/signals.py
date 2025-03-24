from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Project, Contributor, Issue, Comment

def get_related_users(instance):
    """Identify users affected by model changes for cache invalidation"""
    if isinstance(instance, Project):
        return [instance.author.id] + list(instance.contributors.values_list('user_id', flat=True))

    elif isinstance(instance, Contributor):
        return [instance.project.author.id] + list(
            instance.project.contributors.values_list('user_id', flat=True)
        )

    elif isinstance(instance, Issue):
        return [instance.project.author.id] + list(
            instance.project.contributors.values_list('user_id', flat=True)
        )

    elif isinstance(instance, Comment):
        return [instance.issue.project.author.id] + list(
            instance.issue.project.contributors.values_list('user_id', flat=True)
        )

    return []

@receiver([post_save, post_delete], sender=Project)
@receiver([post_save, post_delete], sender=Contributor)
@receiver([post_save, post_delete], sender=Issue)
@receiver([post_save, post_delete], sender=Comment)
def auto_invalidate_cache(sender, instance, **kwargs):
    """Global cache invalidation signal handler"""
    users = get_related_users(instance)
    keys_to_delete = []
    for user_id in users:
        keys_to_delete.extend([
            f"projects_list_user_{user_id}_v2",
            f"contributors_list_user_{user_id}_v2",
            f"issues_list_user_{user_id}_v2",
            f"comments_list_user_{user_id}_v2"
        ])
    if keys_to_delete:
        cache.delete_many(set(keys_to_delete))
