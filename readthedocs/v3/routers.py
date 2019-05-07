from rest_framework.routers import APIRootView, DefaultRouter
from rest_framework_extensions.routers import NestedRouterMixin


class DocsAPIRootView(APIRootView):

    # Overridden only to add documentation for BrowsableAPIRenderer.

    """
    Read the Docs APIv3 root endpoint.

    Full documentation at [https://docs.readthedocs.io/en/latest/api/v3.html](https://docs.readthedocs.io/en/latest/api/v3.html).
    """

    def get_view_name(self):
        return 'Read the Docs APIv3'


class DefaultRouterWithNesting(NestedRouterMixin, DefaultRouter):
    APIRootView = DocsAPIRootView
    root_view_name = 'api-v3-root'
