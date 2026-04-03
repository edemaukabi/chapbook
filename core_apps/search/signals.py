import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django_elasticsearch_dsl.registries import registry

from core_apps.articles.models import Article

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Article)
def update_document(sender, instance=None, created=False, **kwargs):
    """Update the ArticleDocument in Elasticsearch when an article instance is updated or created."""
    try:
        registry.update(instance)
    except Exception as e:
        # Never let an ES indexing failure block article creation/update
        logger.warning(f"Elasticsearch indexing failed for article {instance.pk}: {e}")


@receiver(post_delete, sender=Article)
def delete_document(sender, instance=None, **kwargs):
    """Delete the ArticleDocument in Elasticsearch when an article instance is deleted."""
    try:
        registry.delete(instance)
    except Exception as e:
        logger.warning(f"Elasticsearch delete failed for article {instance.pk}: {e}")
