import datetime
import urllib

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_flex_fields import FlexFieldsModelSerializer
from rest_flex_fields.serializers import FlexFieldsSerializerMixin
from rest_framework import serializers

from readthedocs.builds.models import Build, Version
from readthedocs.projects.constants import LANGUAGES, PROGRAMMING_LANGUAGES
from readthedocs.projects.models import Project


class UserSerializer(FlexFieldsModelSerializer):

    # TODO: return ``null`` when ``last_name`` or ``first_name`` are `''``. I'm
    # thinking on writing a decorator or similar that dynamically creates the
    # methods based on a field with a list

    class Meta:
        model = User
        fields = [
            'username',
            'date_joined',
            'last_login',
            'first_name',
            'last_name',
        ]


class BaseLinksSerializer(serializers.Serializer):

    def _absolute_url(self, path):
        scheme = 'http' if settings.DEBUG else 'https'
        domain = settings.PRODUCTION_DOMAIN
        return urllib.parse.urlunparse((scheme, domain, path, '', '', ''))


class BuildTriggerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Build
        fields = []


class BuildLinksSerializer(BaseLinksSerializer):
    _self = serializers.SerializerMethodField()
    version = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()

    def get__self(self, obj):
        path = reverse(
            'projects-builds-detail',
            kwargs={
                'parent_lookup_project__slug': obj.project.slug,
                'build_pk': obj.pk,
            },
        )
        return self._absolute_url(path)

    def get_version(self, obj):
        path = reverse(
            'projects-versions-detail',
            kwargs={
                'parent_lookup_project__slug': obj.project.slug,
                'version_slug': obj.version.slug,
            },
        )
        return self._absolute_url(path)

    def get_project(self, obj):
        path = reverse(
            'projects-detail',
            kwargs={
                'project_slug': obj.project.slug,
            },
        )
        return self._absolute_url(path)


class BuildConfigSerializer(FlexFieldsSerializerMixin, serializers.Serializer):

    def to_representation(self, obj):
        # For now, we want to return the ``config`` object as it is without
        # manipulating it.
        return obj


class BuildStateSerializer(serializers.Serializer):
    code = serializers.CharField(source='state')
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.state.title()


class BuildSerializer(FlexFieldsModelSerializer):

    project = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    version = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    created = serializers.DateTimeField(source='date')
    finished = serializers.SerializerMethodField()
    duration = serializers.IntegerField(source='length')
    state = BuildStateSerializer(source='*')
    links = BuildLinksSerializer(source='*')

    expandable_fields = dict(
        config=(
            BuildConfigSerializer,
            dict(
                source='config',
            ),
        ),
    )

    class Meta:
        model = Build
        fields = [
            'id',
            'version',
            'project',
            'created',
            'finished',
            'duration',
            'state',
            'success',
            'error',
            'commit',
            'builder',
            'cold_storage',
            'links',
        ]

    def get_finished(self, obj):
        if obj.date and obj.length:
            return obj.date + datetime.timedelta(seconds=obj.length)


class PrivacyLevelSerializer(serializers.Serializer):
    code = serializers.CharField(source='privacy_level')
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.privacy_level.title()


class VersionLinksSerializer(BaseLinksSerializer):
    _self = serializers.SerializerMethodField()
    builds = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()

    def get__self(self, obj):
        path = reverse(
            'projects-versions-detail',
            kwargs={
                'parent_lookup_project__slug': obj.project.slug,
                'version_slug': obj.slug,
            },
        )
        return self._absolute_url(path)

    def get_builds(self, obj):
        path = reverse(
            'projects-versions-builds-list',
            kwargs={
                'parent_lookup_project__slug': obj.project.slug,
                'parent_lookup_version__slug': obj.slug,
            },
        )
        return self._absolute_url(path)

    def get_project(self, obj):
        path = reverse(
            'projects-detail',
            kwargs={
                'project_slug': obj.project.slug,
            },
        )
        return self._absolute_url(path)


class VersionURLsSerializer(serializers.Serializer):
    documentation = serializers.SerializerMethodField()
    vcs = serializers.URLField(source='vcs_url')

    def get_documentation(self, obj):
        return obj.project.get_docs_url(version_slug=obj.slug,)


class VersionSerializer(FlexFieldsModelSerializer):

    privacy_level = PrivacyLevelSerializer(source='*')
    ref = serializers.CharField()
    downloads = serializers.SerializerMethodField()
    urls = VersionURLsSerializer(source='*')
    links = VersionLinksSerializer(source='*')

    expandable_fields = dict(
        last_build=(
            BuildSerializer,
            dict(
                source='last_build',
            ),
        ),
    )

    class Meta:
        model = Version
        fields = [
            'id',
            'slug',
            'verbose_name',
            'identifier',
            'ref',
            'built',
            'active',
            'uploaded',
            'privacy_level',
            'type',
            'downloads',
            'urls',
            'links',
        ]

    def get_downloads(self, obj):
        downloads = obj.get_downloads()
        data = {}

        for k, v in downloads.items():
            if k in ('htmlzip', 'pdf', 'epub'):
                data[k] = ('http:' if settings.DEBUG else 'https:') + v

        return data


class VersionUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Version
        fields = [
            'active',
            'privacy_level',
        ]


class LanguageSerializer(serializers.Serializer):

    code = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_code(self, language):
        return language

    def get_name(self, language):
        for code, name in LANGUAGES:
            if code == language:
                return name
        return 'Unknown'


class ProgrammingLanguageSerializer(serializers.Serializer):

    code = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    def get_code(self, programming_language):
        return programming_language

    def get_name(self, programming_language):
        for code, name in PROGRAMMING_LANGUAGES:
            if code == programming_language:
                return name
        return 'Unknown'


class ProjectURLsSerializer(serializers.Serializer):
    documentation = serializers.CharField(source='get_docs_url')
    project = serializers.SerializerMethodField()

    def get_project(self, obj):
        # Overridden only to return ``None`` when the description is ``''``
        return obj.project_url or None


class RepositorySerializer(serializers.Serializer):

    url = serializers.CharField(source='repo')
    type = serializers.CharField(source='repo_type')


class ProjectLinksSerializer(BaseLinksSerializer):

    _self = serializers.SerializerMethodField()

    users = serializers.SerializerMethodField()
    versions = serializers.SerializerMethodField()
    builds = serializers.SerializerMethodField()
    subprojects = serializers.SerializerMethodField()
    superproject = serializers.SerializerMethodField()
    translations = serializers.SerializerMethodField()

    def get__self(self, obj):
        path = reverse('projects-detail', kwargs={'project_slug': obj.slug})
        return self._absolute_url(path)

    def get_users(self, obj):
        path = reverse(
            'projects-users-list',
            kwargs={
                'parent_lookup_projects__slug': obj.slug,
            },
        )
        return self._absolute_url(path)

    def get_versions(self, obj):
        path = reverse(
            'projects-versions-list',
            kwargs={
                'parent_lookup_project__slug': obj.slug,
            },
        )
        return self._absolute_url(path)

    def get_builds(self, obj):
        path = reverse(
            'projects-builds-list',
            kwargs={
                'parent_lookup_project__slug': obj.slug,
            },
        )
        return self._absolute_url(path)

    def get_subprojects(self, obj):
        path = reverse(
            'projects-subprojects',
            kwargs={
                'project_slug': obj.slug,
            },
        )
        return self._absolute_url(path)

    def get_superproject(self, obj):
        path = reverse(
            'projects-superproject',
            kwargs={
                'project_slug': obj.slug,
            },
        )
        return self._absolute_url(path)

    def get_translations(self, obj):
        path = reverse(
            'projects-translations',
            kwargs={
                'project_slug': obj.slug,
            },
        )
        return self._absolute_url(path)


class ProjectSerializer(FlexFieldsModelSerializer):

    language = LanguageSerializer()
    programming_language = ProgrammingLanguageSerializer()
    repository = RepositorySerializer(source='*')
    privacy_level = PrivacyLevelSerializer(source='*')
    urls = ProjectURLsSerializer(source='*')
    subproject_of = serializers.SerializerMethodField()
    translation_of = serializers.SerializerMethodField()
    default_branch = serializers.CharField(source='get_default_branch')
    tags = serializers.StringRelatedField(many=True)

    description = serializers.SerializerMethodField()

    links = ProjectLinksSerializer(source='*')

    # TODO: adapt these fields with the proper names in the db and then remove
    # them from here
    created = serializers.DateTimeField(source='pub_date')
    modified = serializers.DateTimeField(source='modified_date')

    expandable_fields = dict(
        users=(
            UserSerializer,
            dict(
                source='users',
                many=True,
            ),
        ),
        active_versions=(
            VersionSerializer,
            dict(
                # NOTE: this has to be a Model method, can't be a
                # ``SerializerMethodField`` as far as I know
                source='active_versions',
                many=True,
            ),
        ),
    )

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'created',
            'modified',
            'language',
            'programming_language',
            'repository',
            'default_version',
            'default_branch',
            'privacy_level',
            'subproject_of',
            'translation_of',
            'urls',
            'tags',

            # NOTE: ``expandable_fields`` must not be included here. Otherwise,
            # they will be tried to be rendered and fail
            # 'users',
            # 'active_versions',

            'links',
        ]

    def get_description(self, obj):
        # Overridden only to return ``None`` when the description is ``''``
        return obj.description or None

    def get_translation_of(self, obj):
        try:
            return obj.main_language_project.slug
        except Exception:
            return None

    def get_subproject_of(self, obj):
        try:
            return obj.superprojects.first().slug
        except Exception:
            return None
