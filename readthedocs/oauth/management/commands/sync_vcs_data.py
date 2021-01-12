from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from readthedocs.oauth.tasks import sync_remote_repositories


class Command(BaseCommand):
    help = "Sync OAuth RemoteRepository and RemoteOrganization"

    def add_arguments(self, parser):
        parser.add_argument(
            '--queue',
            type=str,
            default='resync-oauth',
            help='Celery queue name.',
        )
        parser.add_argument(
            '--users',
            nargs='+',
            type=str,
            default=[],
            help='Re-sync VCS provider data for specific users only.',
        )
        parser.add_argument(
            '--skip-users',
            nargs='+',
            type=str,
            default=[],
            help='Skip re-sync VCS provider data for specific users.',
        )
        parser.add_argument(
            '--max-users',
            type=int,
            default=100,
            help='Maximum number of users that should be synced.',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help='Force re-sync VCS provider data even if the users are already synced.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=False,
            help='Do not trigger tasks for VCS provider re-sync.',
        )

    def handle(self, *args, **options):
        queue = options.get('queue')
        sync_users = options.get('users')
        skip_users = options.get('skip_users')
        max_users = options.get('max_users')
        force_sync = options.get('force')
        dry_run = options.get('dry_run')

        # Filter users who have social accounts connected to their RTD account
        users = User.objects.filter(
            socialaccount__isnull=False
        ).distinct()

        if not force_sync:
            users = users.filter(
                remote_repository_relations__isnull=True
            ).distinct()

        self.stdout.write(
            self.style.SUCCESS(
                f'Total {users.count()} user(s) can be synced'
            )
        )

        if sync_users:
            users = users.filter(username__in=sync_users)

        if skip_users:
            users = users.exclude(username__in=skip_users)

        if sync_users or skip_users:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Found {users.count()} user(s) with the given parameters'
                )
            )

        # Don't trigger VCS provider re-sync tasks if --dry-run is provided
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    'No VCS provider re-sync task was triggered. '
                    'Run it without --dry-run to trigger the re-sync tasks.'
                )
            )
        else:
            users_to_sync = users.values_list('id', flat=True)[:max_users]

            self.stdout.write(
                self.style.SUCCESS(
                    f'Triggering VCS provider re-sync task(s) for {len(users_to_sync)} user(s)'
                )
            )

            for user_id in users_to_sync:
                # Trigger Sync Remote Repository Tasks for users
                sync_remote_repositories.apply_async(
                    args=[user_id], queue=queue
                )
