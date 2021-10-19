"""Tasks for OAuth services."""

import logging

from allauth.socialaccount.providers import registry as allauth_registry
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from readthedocs.core.permissions import AdminPermission
from readthedocs.core.utils.tasks import PublicTask, user_id_matches
from readthedocs.oauth.notifications import (
    AttachWebhookNotification,
    InvalidProjectWebhookNotification,
)
from readthedocs.oauth.services.base import SyncServiceError
from readthedocs.oauth.utils import SERVICE_MAP
from readthedocs.projects.models import Project
from readthedocs.worker import app

from .services import registry


log = logging.getLogger(__name__)


@PublicTask.permission_check(user_id_matches)
@app.task(queue='web', base=PublicTask)
def sync_remote_repositories(user_id):
    user = User.objects.filter(pk=user_id).first()
    if not user:
        return

    # TODO: remove this log once we find out what's causing OOM
    log.info('Running readthedocs.oauth.tasks.sync_remote_repositories. locals=%s', locals())

    failed_services = set()
    for service_cls in registry:
        for service in service_cls.for_user(user):
            try:
                service.sync()
            except SyncServiceError:
                failed_services.add(service.provider_name)
    if failed_services:
        msg = _(
            'Our access to your following accounts was revoked: {providers}. '
            'Please, reconnect them from your social account connections.'
        )
        raise Exception(
            msg.format(providers=', '.join(failed_services))
        )


@app.task(queue='web')
def sync_remote_repositories_organizations():
    """
    Re-sync users member of organizations with SSO enabled.

    It will trigger one `sync_remote_repositories` task per user.
    """
    query = (
        SSOIntegration.objects
        .filter(provider=SSOIntegration.PROVIDER_ALLAUTH)
        .values_list('organization', flat=True)
    )
    log.info('Triggering scheduled SSO re-sync for all organizations. count=%s', query.count())
    for organization in query:
        members = AdminPermission.members(organization)
        log.info(
            'Triggering scheduled SSO re-sync for organization. organization=%s users=%s',
            organization.slug,
            members.count(),
        )
        for user in members:
            sync_remote_repositories.delay(user.pk)


@app.task(queue='web')
def attach_webhook(project_pk, user_pk, integration=None):
    """
    Add post-commit hook on project import.

    This is a brute force approach to add a webhook to a repository. We try
    all accounts until we set up a webhook. This should remain around for legacy
    connections -- that is, projects that do not have a remote repository them
    and were not set up with a VCS provider.
    """
    project = Project.objects.filter(pk=project_pk).first()
    user = User.objects.filter(pk=user_pk).first()

    if not project or not user:
        return False

    project_notification = InvalidProjectWebhookNotification(
        context_object=project,
        user=user,
        success=False,
    )
    if integration:
        service = SERVICE_MAP.get(integration.integration_type)

        if not service:
            log.warning('There are no registered services in the application.')
            project_notification.send()
            return None
    else:
        for service_cls in registry:
            if service_cls.is_project_service(project):
                service = service_cls
                break
        else:
            log.warning('There are no registered services in the application.')
            project_notification.send()
            return None

    provider = allauth_registry.by_id(service.adapter.provider_id)
    notification = AttachWebhookNotification(
        context_object=provider,
        extra_context={'project': project},
        user=user,
        success=None,
    )

    user_accounts = service.for_user(user)
    for account in user_accounts:
        success, __ = account.setup_webhook(project, integration=integration)
        if success:
            notification.success = True
            notification.send()

            project.has_valid_webhook = True
            project.save()
            return True

    # No valid account found
    if user_accounts:
        notification.success = False
        notification.reason = AttachWebhookNotification.NO_PERMISSIONS
    else:
        notification.success = False
        notification.reason = AttachWebhookNotification.NO_ACCOUNTS

    project_notification.send()
    notification.send()
    return False
