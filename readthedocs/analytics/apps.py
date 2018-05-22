"""Django app config for the analytics app."""

from __future__ import absolute_import
from django.apps import AppConfig


class AnalyticsAppConfig(AppConfig):

    """Analytics app init code"""

    name = 'readthedocs.analytics'
    verbose_name = 'Analytics'

    def ready(self):
        """Fired once during Django startup"""
        import readthedocs.analytics.signals  # noqa
