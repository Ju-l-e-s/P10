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

def increment_version(key_prefix, user_id):
    version_key = f"{key_prefix}_version_user_{user_id}"
    version = cache.get(version_key) or 1
    cache.set(version_key, version + 1, None)
    return version + 1

@receiver([post_save, post_delete], sender=Project)
@receiver([post_save, post_delete], sender=Contributor)
@receiver([post_save, post_delete], sender=Issue)
@receiver([post_save, post_delete], sender=Comment)
def auto_invalidate_cache(sender, instance, **kwargs):
    """Invalidate all pages by incrementing the cache version for each endpoint"""
    users = get_related_users(instance)
    for user_id in users:
        for prefix in ["projects_list", "contributors_list", "issues_list", "comments_list"]:
            increment_version(prefix, user_id)
