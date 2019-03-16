# -*- coding: utf-8 -*-

"""Template tags to query projects by privacy."""

from django import template
from django.db.models import Exists, OuterRef, Subquery

from readthedocs.builds.models import Build
from readthedocs.core.permissions import AdminPermission
from readthedocs.projects.models import Project


register = template.Library()


@register.filter
def is_admin(user, project):
    return AdminPermission.is_admin(user, project)


@register.simple_tag(takes_context=True)
def get_public_projects(context, user):
    builds = Build.objects.filter(project=OuterRef('pk'))
    date_sub_query = Subquery(builds.values('date')[:1])
    projects = Project.objects.for_user_and_viewer(
        user=user,
        viewer=context['request'].user,
    ).prefetch_related('users').annotate(
        latest_build_date=date_sub_query,
        good_build=Exists(builds.filter(success=True)))
    context['public_projects'] = projects
    return ''
