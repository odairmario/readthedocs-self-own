"""We define custom Django signals to trigger before executing searches."""
from __future__ import absolute_import
import django.dispatch
from django.dispatch import receiver
from django_elasticsearch_dsl.registries import registry

from readthedocs.projects.models import HTMLFile
from readthedocs.projects.signals import bulk_post_create, bulk_post_delete
from readthedocs.search.documents import PageDocument
from readthedocs.search.tasks import index_objects_to_es_task

before_project_search = django.dispatch.Signal(providing_args=["body"])
before_file_search = django.dispatch.Signal(providing_args=["body"])
before_section_search = django.dispatch.Signal(providing_args=["body"])


@receiver(bulk_post_create, sender=HTMLFile)
def index_html_file(instance_list, **_):
    kwargs = {
        'app_label': HTMLFile._meta.app_label,
        'model_name': HTMLFile.__name__,
        'document_class': str(PageDocument),
        'index_name': None,  # No neeed to change the index name
        'objects_id': [obj.id for obj in instance_list],
    }

    index_objects_to_es_task.delay(**kwargs)


@receiver(bulk_post_delete, sender=HTMLFile)
def remove_html_file(instance_list, **_):
    registry.delete(instance_list)
