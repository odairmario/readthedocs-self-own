"""Objects for User permission checks."""
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q

from readthedocs.core.utils.extend import SettingsOverrideObject


class AdminPermissionBase:

    @classmethod
    def owners(cls, obj):
        """
        Return the owners of `obj`.

        If organizations are enabled,
        we return the owners of the project organization instead.
        """
        from readthedocs.organizations.models import Organization
        from readthedocs.projects.models import Project

        if isinstance(obj, Project):
            if settings.RTD_ALLOW_ORGANIZATIONS:
                obj = obj.organizations.first()
            else:
                return obj.users.all()

        if isinstance(obj, Organization):
            return obj.owners.all()

    @classmethod
    def admins(cls, obj):
        from readthedocs.organizations.models import Organization
        from readthedocs.projects.models import Project

        if isinstance(obj, Project):
            return obj.users.all()

        if isinstance(obj, Organization):
            return obj.owners.all()

    @classmethod
    def members(cls, obj):
        from readthedocs.organizations.models import Organization
        from readthedocs.projects.models import Project

        if isinstance(obj, Project):
            return obj.users.all()

        if isinstance(obj, Organization):
            return User.objects.filter(
                Q(teams__organization=obj) | Q(owner_organizations=obj),
            ).distinct()

    @classmethod
    def is_admin(cls, user, obj):
        # This explicitly uses "user in project.users.all" so that
        # users on projects can be cached using prefetch_related or prefetch_related_objects
        return user in cls.admins(obj) or user.is_superuser

    @classmethod
    def is_member(cls, user, obj):
        return user in cls.members(obj) or user.is_superuser


class AdminPermission(SettingsOverrideObject):
    _default_class = AdminPermissionBase
    _override_setting = 'ADMIN_PERMISSION'
